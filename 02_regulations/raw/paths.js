function Paths() {}

Paths.getModulesPath = function () {
    return getCustomPath()

    function getCustomPath() {
        // modules path relative to index.html
        var relativePath = "/modules/"

        // application url containing url parameters
        if (window.location.href.indexOf("index") > -1) {
            var appUrl = window.location.href.replace(/index(\S+).html/, "")
        } else {
            var appUrl = window.location.href
        }

        // remove url parameters from the url
        if (appUrl.indexOf("?") !== -1) {
            appUrl = appUrl.substring(0, appUrl.indexOf("?"))
        }

        if (window.location.href.indexOf("#tcz") > -1) {
            appUrl = appUrl.split("#")[0]
        }

        // remove keycloak paramteres
        if (appUrl.indexOf("#") > -1) {
            appUrl = appUrl.substring(0, appUrl.indexOf("#"))
        }

        return appUrl.split("index")[0] + relativePath
    }
}

Paths.getPrivateModulesPath = function () {
    // modules path relative to index.html
    var relativePath = "/js/"

    if (window.location.href.indexOf("index") > -1) {
        var appUrl = window.location.href.replace(/index(\S+).html/, "")
    } else {
        var appUrl = window.location.href
    }

    // remove url parameters from the url
    if (appUrl.indexOf("?") !== -1) {
        appUrl = appUrl.substring(0, appUrl.indexOf("?"))
    }

    if (window.location.href.indexOf("#tcz") > -1) {
        appUrl = appUrl.split("#")[0]
    }

    // remove keycloak paramteres
    if (appUrl.indexOf("#") > -1) {
        appUrl = appUrl.substring(0, appUrl.indexOf("#"))
    }
    return appUrl.split("index")[0] + relativePath
}

Paths.getTranslationsPath = function () {
    return Paths.getModulesPath() + "json/translations.json"
}

Paths.getSourcesPath = function () {
    /* if (window.location.href.includes("appt")) {
        return "https://appt.iprpraha.cz/apl-dev/_src/sources.json"
    }
    return "https://app.iprpraha.cz/apl/_src/sources.json" */
    return "./conf/sources.json"
}

Paths.getTokensPath = function () {
    return "https://geoportalpraha.cz/backend/get-tokens"
    // return "./conf/tokens.json"
}
