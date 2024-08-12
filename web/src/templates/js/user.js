var userMethods = {
    initUser() {
        console.log("init");
        // Check if accessing via nvidia.com
        if (window.location['host'].includes('nvidia.com')) {
            // Check if s_ecid Adobe cookie exists. 
            let adobeCookie = this.getCookie('s_ecid');
            if (adobeCookie === undefined) {
                adobeCookie = this.getCookie('s_vi');
                if (adobeCookie === undefined) {
                    adobeCookie = this.getCookie('s_fid');
                    if (adobeCookie === undefined) {
                        adobeCookie = this.getCookie('_cs_id');
                    }
                }
            }

            console.log('Adobe cookie: ', adobeCookie);
            if (adobeCookie === undefined) {
                console.log('Problem getting Adobe cookie');
                // Prompt for username
                this.showUsernameModal();
            } else {
                this.s_ecid = adobeCookie;
                // Check if this cookie can be associated with username
                this.getUsername();
            }

        } else {  // local development
            this.username = 'dev';  
            this.s_ecid = 'devcookie';
            this.getUsername();
        }
    },
    getCookie(cookieName) {
        // https://stackoverflow.com/a/15724300
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${cookieName}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    },
    showUsernameModal() {
        if (document.readyState === "complete" || document.readyState === "interactive") {
            // call on next available tick
            setTimeout(this.showUsernameModalHelper, 1);
        } else {
            document.addEventListener("DOMContentLoaded", this.showUsernameModalHelper);
        }
    },
    showUsernameModalHelper() {
        let myModal = new bootstrap.Modal(document.getElementById("usernameModal"), {});
        myModal.show();
    },
    getUsername() {
        if (this.s_ecid !== '') {
            console.log('Sending GET request to /user with s_ecid: ', this.s_ecid);
            axios.get("/user", {
                params: {'s_ecid': this.s_ecid}
            }).then(response => {
                console.log('GET /user response: ', response);
                let responseUsername = response['data']['username'];
                if (responseUsername != null && responseUsername !== '') {
                    this.username = responseUsername
                } else {
                    // If no match, prompt for username
                    this.showUsernameModal();
                }
            }).catch(error => {
                console.log(error);
            });
        }
        
    },
    postUsername() {
        if (this.s_ecid !== '') {
            axios.post("/user", {
                s_ecid: this.s_ecid,
                username: this.username
            })
            .then(function(response) {
                console.log(response);
            })
            .catch(function(error) {
                console.log(error);
            });
        }
    },
    logQuery(queryType, query) {
        if (queryType !== '' && query !== '') {
            axios.post("/logquery", {
                s_ecid: this.s_ecid,
                queryType: queryType,
                query: query,
            });
        }
    }
};
