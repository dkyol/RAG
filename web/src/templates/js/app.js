{% include 'js/user.js' %}

// Static Data Populated by Jinja
var all_asset_types = {{ all_asset_types | tojson}};

// Event Source used to set up connection with Flask
var source;

smoothScroll = function(selector) {
    document.querySelector(selector).scrollIntoView({
        behavior: 'smooth'
    });
};

scrollToCitation = function(event, idx) {
    smoothScroll("#result_title_" + idx);
    event.preventDefault();
};

// Vue application
var app = new Vue({
    el: '#app',
    data: {
        // This is static (used to be dynamic so we could switch to tagpredict)
        recType: 'text',

        // Static session ID
        session_id: '',

        // Inputs
        query: `{{ query }}`,
        k: '{{ k }}',
        model_name: `{{ model_name }}`,

        // Asset Types
        asset_types: all_asset_types,

        // Store and present the response from the app
        results: [],
        response_asset_types: [],
        response_display_titles: [],
        results_visible: [],
        generation: '',
        query_expansion: '',

        username: '',
        s_ecid: '',
    },
    created: function() {
        console.log('Vue instance created'); 
        this.initUser();
        if (this.query !== '') {
            console.log('Submitting form with query params');
            this.submitForm();
        } else {
            setTimeout(this.hideLoader, 100);
        }

        
        setTimeout( function() {
            document.getElementById('app').classList.remove('d-none');  // only show app when it's ready
        }, 101);

    },
    delimiters: ['[[', ']]'],  // because Jinja uses curly brackets
    computed: {
        asset_type_groups() {
            let ret = [];
            for (let i = 0; i < this.asset_types.length; i++) {
                if (ret.length === 0 || ret[ret.length - 1]["group"] !== this.asset_types[i]["group"]) {
                    ret.push({
                        "group": this.asset_types[i]["group"],
                        "group_sort_order": this.asset_types[i]["group_sort_order"],
                        "group_members": [this.asset_types[i]]
                    });
                } else {
                    ret[ret.length - 1]["group_members"].push(this.asset_types[i]);
                }
            }
            return ret;
        }
    },
    methods: {
        toggleAssetTypeGroup(group, event) {
            let behavior;
            for (let i = 0; i < this.asset_types.length; i++) {
                if (group == null || this.asset_types[i]['group'] === group) {
                    if (typeof behavior === 'undefined') {
                        behavior = !this.asset_types[i]['display'];
                    }
                    this.asset_types[i]['display'] = behavior;
                }
            }
            event.preventDefault();
        },
        submitForm() {
            console.log('submit: ', this.query, this.k);

            // Clear generation first
            this.generation = '';

            // Create a new session id
            this.session_id = this.uuidv4()

            // Add event source and listeners
            source = new EventSource("/stream?channel=generate." + this.session_id);
            source.addEventListener('greeting', (event) => {
                let data = JSON.parse(event.data);
                console.log("Greeting: " + data.message);

                // Fill results with documents related to query
                let greeting = JSON.parse(data.message);
                this.results = 'results' in greeting ? greeting['results'] : [];
                this.response_asset_types = 'asset_types' in greeting ? greeting['asset_types'] : [];
                this.response_display_titles = 'display_titles' in greeting ? greeting['display_titles'] : [];
                this.results_visible = new Array(this.results.length).fill(true);
                this.hideLoader();
                setTimeout(smoothScroll, 150, '#appOutput');
            }, false);
            source.addEventListener('publish', (event) => {
                let data = JSON.parse(event.data);
                // console.log("Publish: " + data.message);
                this.generation += data.message;
            }, false);
            source.addEventListener('error', (event) => {
                console.log("Error");
            }, false);  

            // clear query expansion
            this.query_expansion = '';

            let ajaxUrl = '/generate';

            let ajaxAssetTypes = [];
            for (let i = 0; i < this.asset_types.length; i++) {
                if (this.asset_types[i]['display']) {
                    ajaxAssetTypes.push(this.asset_types[i]['name']);
                }
            }

            if (ajaxAssetTypes.length === 0) {
                return; // end function early
            }

            let ajaxParams = {
                'query': this.query, 
                'k': this.k,
                'session_id': this.session_id,
                'asset_types': ajaxAssetTypes,
                'model_name': this.model_name
            };
            
            this.showLoader();
            axios.post(ajaxUrl, ajaxParams).then(response => {
                console.log("submitForm response: ", response);
                this.generation = response['data']['generation'];     
            }).catch(error => {
                console.log(error);
                this.results = [{"title": "Error", "blurb": "Error"}];
                this.response_asset_types = [];
                this.response_display_titles = [];
                this.generation = '';
            }).finally( () => {
                this.hideLoader();  // may be unnecessary
            });

            this.logQuery(this.recType, JSON.stringify(ajaxParams));


        },
        removeAsset(idx) {
            let asset_type = this.response_asset_types[idx];
            console.log(asset_type);
            for (let i = 0; i < this.asset_types.length; i++) {
                if (this.asset_types[i]['name'] === asset_type ) {
                    this.asset_types[i]['display'] = false;
                    break;
                }
            }
            setTimeout(this.submitForm, 150);
        },
        toggleAssetVisibility(idx) {
            this.results_visible[idx] = !this.results_visible[idx]; 
            this.$forceUpdate();
        },
        toggleAllAssetVisibility() {
            if (this.results_visible.every((x) => x )) {
                this.results_visible = new Array(this.results.length).fill(false);
            } else {
                this.results_visible = new Array(this.results.length).fill(true);
            }
        },
        hideLoader() {
            document.getElementById('loader').classList.add('d-none');  
        },
        showLoader() {
            document.getElementById('loader').classList.remove('d-none');  
        },
        copyLinkToRecs() {
            let url = `${location.protocol}//${location.host}?query=${encodeURIComponent(this.query)}&k=${encodeURIComponent(this.k)}`;
            for (let i = 0; i < this.asset_types.length; i++) {
                if (this.asset_types[i]['display']) {
                    url += `&asset_types=${encodeURIComponent(this.asset_types[i]['name'])}`;
                }
            }
            
            document.getElementById("linkToRecs").innerHTML = url;
            this.copyToClipboard("linkToRecs");
        },
        copyAllRecs() {
            for (let i = 0; i < this.results.length; i++) {
                if (!this.results_visible[i]) {
                    this.toggleAssetVisibility(i);
                }
            }

            setTimeout(this.copyAllRecsInner, 150);
        },
        copyAllRecsInner() {
            var rec_text = "";
            for (let i = 0; i < this.results.length; i++) {
                rec_text += document.getElementById("recs-container-" + i).innerHTML + "<br>";
            }
            document.getElementById("allRecs").innerHTML = rec_text;
            this.copyToClipboard("allRecs");
            document.getElementById("allRecs").innerHTML = "";
        },
        copyRecs(idx) {
            if (!this.results_visible[idx]) {
                this.toggleAssetVisibility(idx);
            }

            let containerId = 'recs-container-' + idx;
            setTimeout(this.copyToClipboard, 150, containerId);
        },
        copyToClipboard(containerId) {
            // Based off https://stackoverflow.com/a/48554118
            let text = document.getElementById(containerId), range, selection;
            console.log(text);

            if (document.body.createTextRange) {
                range = document.body.createTextRange();
                range.moveToElementText(text);
                range.select();
            } else if (window.getSelection) {
                selection = window.getSelection();
                range = document.createRange();
                range.selectNodeContents(text);
                selection.removeAllRanges();
                selection.addRange(range);
            }
            document.execCommand('copy');
            window.getSelection().removeAllRanges();

            document.getElementById('copyAlert').classList.add("show");
            setTimeout(function() {
                document.getElementById('copyAlert').classList.remove("show")
                }, 1500);

            // event.preventDefault();
        },
        reset() {
            this.query = '';
            this.k = '5';
            this.results = [];
            this.response_asset_types = [];
            this.response_display_titles = [];
            this.results_visible = []
            this.asset_types = all_asset_types;
            this.generation = '';
            this.query_expansion = '';
        },
        uuidv4() {
            return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
                (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
            );
        },
        ... userMethods
    }
});
