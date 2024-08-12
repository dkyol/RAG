var userMethods = {
    initUser() {
        console.log("initUser");
        // Check if accessing via nvidia.com
        if (window.location['host'].includes('nvidia.com')) {
            // Check if s_ecid Adobe cookie exists. 
            let adobeCookie = this.getCookie('s_ecid');
            let adobeCookieSource = 's_ecid';
            if (adobeCookie === undefined) {
                // Fallback to s_vi
                adobeCookie = this.getCookie('s_vi');
                adobeCookieSource = 's_vi';
                if (adobeCookie === undefined) {
                    // Fallback to s_fid
                    adobeCookie = this.getCookie('s_fid');
                    adobeCookieSource = 's_fid';
                }
            }

            console.log('Adobe cookie: ', adobeCookie);
            if (adobeCookie === undefined) {
                console.log('Problem getting Adobe cookie');
                this.cookie = '';
                this.cookieSource = '';

                // Prompt for username
                // Since this.cookie is now empty string, we won't create a record mapping cookie to username
                this.showUsernameModal();
            } else {
                this.cookie = adobeCookie;
                this.cookieSource = adobeCookieSource;
                // Check if this cookie is associated with username in the db
                this.getUsername();
            }

        } else {  // local development
            this.username = 'dev';  
            this.cookie = 'devcookie';
            this.cookieSource = 'dev';
            // Check if this cookie is associated with username in the db
            this.getUsername();
        }
    },
    getCookie(cookieName) {
        // https://stackoverflow.com/a/15724300
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${cookieName}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    },
    showUsernameModal(event) {
        if (event !== undefined) {
            event.preventDefault();
        }

        if (document.readyState === "complete" || document.readyState === "interactive") {
            // call on next available tick
            setTimeout(this.showUsernameModalHelper, 1);
        } else {
            document.addEventListener("DOMContentLoaded", this.showUsernameModalHelper);
        }
    },

    // called inside of showUsernameModal()
    showUsernameModalHelper() {
        let myModal = new bootstrap.Modal(document.getElementById("usernameModal"), {});
        myModal.show();
    },

    // Check if this cookie is associated with username in the db
    getUsername() {
        if (this.cookie !== '') {
            console.log('Sending GET request to /cookies/' + encodeURIComponent(this.cookie));
            axios.get("{{ url_for('read_cookies') }}" + encodeURIComponent(this.cookie)).then(response => {
                console.log(response);
                console.log("found this cookie in db");
                
                let responseUsername = response['data']['username'];
                if (responseUsername != null && responseUsername !== '') {
                    this.username = responseUsername
                } else {
                    // Not sure if/why this would happen, but if cookie has no username in db, prompt for username
                    this.showUsernameModal();
                }
            }).catch(error => {
                console.log(error);
                console.log("could not find cookie in db");
                
                // If no match, prompt for username
                this.showUsernameModal();
            });
        }
        
    },

    // Associate a cookie with a username
    associateUsername() {
        console.log("associateUsername");
        // Clean up username
        this.username = this.username.trim().toLowerCase();

        if (this.cookie !== '') {
            // First check if this username already exists
            // If not create the user
            axios.get("{{ url_for('read_users') }}" + encodeURIComponent(this.username)).then(response => {
                console.log(response);
                console.log("user already exists");
            }).catch(error => {
                console.log(error);
                console.log("user does not exist. attempting to create");
                
                axios.post("{{ url_for('create_user') }}", {
                    username: this.username
                })
                .then(function(response) {
                    console.log(response);
                    console.log("created new user");
                })
                .catch(function(error) {
                    console.log(error);
                    console.log("error creating new user");
                });
            }).finally(() => {
                // Finally associate cookie with this username
                axios.post("{{ url_for('create_user') }}" + encodeURIComponent(this.username) + "/cookies/", {
                    cookie: this.cookie,
                    cookie_source: this.cookieSource
                })
                .then(function(response) {
                    console.log(response);
                    console.log("associateUsername success");
                })
                .catch(function(error) {
                    console.log(error);
                    console.log("associateUsername error");
                });
            });
            
        }
    }
};
