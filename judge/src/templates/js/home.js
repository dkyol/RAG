// Vue application
var app = new Vue({
    el: '#app',
    data: {
        // ............ STEP 1

        // Input Type Selector
        searchType: '',

        query: '',
        k: '10',
        
        keywordSearchField: 'content',
        keywordSearchType: 'union',

        // ............ STEP 2

        // Asset Types
        asset_types: [],
        
        
        

        

        

        // ........... STEP 3

        // Store and present the response from the app
        results: [],
        response_asset_types: [],
        response_display_titles: [],
        results_visible: [],

        // User tracking
        username: '',
        cookie: '',
        cookieSource: ''
    },

    created: function() {
        console.log('Vue instance created'); 
        this.initUser();
        this.pullAssetTypes();
        setTimeout(this.hideLoader, 100);
        setTimeout( function() {
            document.getElementById('app').classList.remove('d-none');  // only show app when it's ready
        }, 101);
    },
    delimiters: ['[[', ']]'],  // because Jinja uses curly brackets
    methods: {
        pullAssetTypes() {
            let ajaxUrl = "http://localhost:5006/asset-types";
            axios.get(ajaxUrl).then(response => {
                console.log("/asset-types response: ", response);
                let all_asset_types = response.data;
                for (let i = 0; i < all_asset_types.length; i++) {
                    let atype = all_asset_types[i];
                    atype["display"] = atype["display_default"]
                }   
                this.asset_types = all_asset_types;
            }).catch(error => {
                console.log(error);
            });
        },

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

        submit() {
            let text = this.query;

            // strip whitespace
            text = text.trim();

            if (text.length===0) {
                this.reset();
                return
            }

            let ajaxUrl = "http://localhost:5006/search/";
            ajaxUrl = ajaxUrl + this.searchType;

            let ajaxAssetTypes = [];
            for (let i = 0; i < this.asset_types.length; i++) {
                if (this.asset_types[i]['display']) {
                    ajaxAssetTypes.push(this.asset_types[i]['name']);
                }
            }

            if (ajaxAssetTypes.length === 0) {
                this.resetResponseData();
                return; // end function early
            }

            let ajaxJson = {
                'k': this.k,
                'asset_types': ajaxAssetTypes
            };

            if (this.searchType === 'keyword') {
                ajaxJson['search_type'] = this.keywordSearchType;
                ajaxJson['field'] = this.keywordSearchField;
                ajaxJson['value'] = text;
            } else {
                ajaxJson['query'] = text;
            }

            this.showLoader();
            this.resetResponseData();

            console.log(ajaxJson);

            axios.post(ajaxUrl, ajaxJson).then(response => {

                // TODO: Do we still need to reformat into legacy format?
                let results = [];
                let response_asset_types = [];
                let response_display_titles = [];

                console.log("submit /search response: ", response);
                for (let i = 0; i < response['data'].length; i++) {
                    let at_results = response['data'][i]['results'];
                    for (let j = 0; j < at_results.length; j++) {
                        let result = at_results[j];
                        // Replace with first item in list
                        if (result["heading_section_index"] != null && result["heading_section_title"] != null) {
                            let heading_section_index_unique = []
                            let heading_section_title_unique = []
                            let heading_section_index_list = JSON.parse(result["heading_section_index"]);
                            let heading_section_title_list = JSON.parse(result["heading_section_title"])
                            for (let k = 0; k < heading_section_index_list.length; k++) {
                                if (!heading_section_index_unique.includes(heading_section_index_list[k])) {
                                    heading_section_index_unique.push(heading_section_index_list[k]);
                                    heading_section_title_unique.push(heading_section_title_list[k]);
                                }
                            }

                            result["heading_section_index"] = heading_section_index_unique.join(', ');
                            result["heading_section_title"] = heading_section_title_unique.join(', ');
                        }

                        if (result["paragraph_index"] != null) {
                            let paragraph_index_unique = []
                            let paragraph_index_list = JSON.parse(result["paragraph_index"]);
                            for (let k = 0; k < paragraph_index_list.length; k++) {
                                if (!paragraph_index_unique.includes(paragraph_index_list[k])) {
                                    paragraph_index_unique.push(paragraph_index_list[k]);
                                }
                            }
                            result["paragraph_index"] = paragraph_index_list.join(', ');
                        }
                    }

                    results.push(at_results);
                    response_asset_types.push(response['data'][i]['asset_type']);
                    response_display_titles.push(response['data'][i]['display_title']);
                }

                this.results = results;
                this.response_asset_types = response_asset_types;
                this.response_display_titles = response_display_titles;

                this.hideLoader();  
                setTimeout(this.smoothScroll, 150);
            }).catch(error => {
                console.log(error);
                this.resetResponseData();
            }).finally( () => {
                this.results_visible = new Array(this.results.length).fill(true);
                this.hideLoader();
            });
        },

        removeAsset(idx) {
            let asset_type = this.response_asset_types[idx];
            for (let i = 0; i < this.asset_types.length; i++) {
                if (this.asset_types[i]['name'] === asset_type ) {
                    this.asset_types[i]['display'] = false;
                    break;
                }
            }
            setTimeout(this.submit, 150);
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

        copyLinkToRecs() {
            let url = `${location.protocol}//${location.host}?recType=${encodeURIComponent(this.recType)}&input_language=${encodeURIComponent(this.input_language)}&output_language=${encodeURIComponent(this.output_language)}&query=${encodeURIComponent(this.query)}&k=${encodeURIComponent(this.k)}`;
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

        resetResponseData() {
            this.results = [];
            this.response_asset_types = [];
            this.response_display_titles = [];
            this.results_visible = [];
        },
        
        reset() {
            // clear data on reset()
            this.query = '';
            this.resetResponseData();
        },

        showSubmitAlert() {
            document.getElementById('submitAlert').classList.add("show");
            setTimeout(function() {
                document.getElementById('submitAlert').classList.remove("show")
                }, 1500);
        },

        vote(chunk_id, vote_value, asset_type, results_idx, n_results) {
            axios.post(
                "{{ url_for('create_feedback') }}", 
                {
                    'query': this.query.trim(),
                    'chunk_id': chunk_id,
                    'search_type': this.searchType,
                    'keyword_search_field': this.searchType === 'keyword' ? this.keywordSearchField : null,
                    'keyword_search_type': this.searchType === 'keyword' ? this.keywordSearchType: null,
                    'asset_type': asset_type, 
                    'k': this.k,
                    'results_idx': results_idx,
                    'n_results': n_results,
                    'vote_value': vote_value,
                    'username': this.username
                }
            ).then(response => {
                console.log("Vote with value: ", vote_value, " received response: ", response);
                this.showSubmitAlert();
            }).catch(error => {
                console.log(error);
            });
        },

        clickEdit(e, idx, modelIdx) {
            let elem = document.getElementById('edit_' + idx + '_' + modelIdx);
            elem.classList.toggle('d-none');
        },

        submitEdit(e, idx, modelIdx, originalText) {
            let parentElement = document.getElementById('edit_' + idx + '_' + modelIdx);
            let textareaElement = parentElement.querySelector("textarea");
            let textareaContent = textareaElement.value;
            let url;
            if (this.selectedArticle != null) {
                url = this.getSelectedArticleLink()
            } else {
                url = null;
            }

            axios.post(
                "{{ url_for('create_feedback') }}", 
                {
                    'value': 0,
                    'original_text': originalText, 
                    'summary_text': textareaContent,
                    'username': this.username,
                    'url': url 
                }
            ).then(response => {
                console.log("Custom feedback response: ", response);
                this.showSubmitAlert();
            }).catch(error => {
                console.log(error);
            });
        },

        hideLoader() {
            document.getElementById('loader').classList.add('d-none');  
        },

        showLoader() {
            document.getElementById('loader').classList.remove('d-none');  
        },

        showSubmitModal() {
            if (document.readyState === "complete" || document.readyState === "interactive") {
                // call on next available tick
                setTimeout(this.showSubmitModalHelper, 1);
            } else {
                document.addEventListener("DOMContentLoaded", this.showSubmitModalHelper);
            }
        },
        showSubmitModalHelper() {
            let myModal = new bootstrap.Modal(document.getElementById("submitModal"), {});
            myModal.show();
        },
        showErrorModal() {
            if (document.readyState === "complete" || document.readyState === "interactive") {
                // call on next available tick
                setTimeout(this.showErrorModalHelper, 1);
            } else {
                document.addEventListener("DOMContentLoaded", this.showErrorModalHelper);
            }
        },
        showErrorModalHelper() {
            let myModal = new bootstrap.Modal(document.getElementById("errorModal"), {});
            myModal.show();
        },
        smoothScroll() {
            document.querySelector('#appOutput').scrollIntoView({
                behavior: 'smooth'
            });
        },
        ... userMethods
    },
    computed: {
        submitDisabled() {
            return this.query === '';
        },
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
    }
});