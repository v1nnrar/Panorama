var kryciListyBaseUrl =
    "https://ppstaticcontentprod.azureedge.net/public/pmp/appdata/klz"
// var kryciListyBaseUrl = "https://files.iprpraha.cz/files/mpp/KLZ"

var identifyConfig = {
    indexes: {
        lokality: 0,
        // "transf_uzemi": 1,
        lokality_kl: 0,
    },

    sourceIds: [
        "mpp_identify/11",
        // "mpp_info_vp/1",
        "mpp_identify/11",
    ],

    templates: {
        lokality:
            "<div class='infoPopupContent'><div class='infoPopupItem' id='infoPopupItem_%LOKALITA%'><ul>",
        // "transf_uzemi": "<div class='infoPopupContent'><div class='infoPopupItem' id='infoPopupItem_%CISLO_TXT%'><ul>",
        lokality_kl: [
            "<div class='infoPopupContent'><div class='infoPopupItem' id='infoPopupItem_%LOKALITA%'><ul><li class='infoPopupItemTitle' id='infoPopupItemTitle_%LOKALITA%'><a href='" +
                kryciListyBaseUrl +
                "/%LOKALITA%.pdf' target='_blank'><img src='img/download.svg'>Stáhnout krycí list pro lokalitu %LOKALITA%</a></li></ul></div>",
            "<div class='infoPopupContent'><div class='infoPopupItem' id='infoPopupItem_%LOKALITA%'><ul><li class='infoPopupItemTitle' id='infoPopupItemTitle_%LOKALITA%'><a href='" +
                kryciListyBaseUrl +
                "/%LOKALITA%.pdf' target='_blank'><img src='img/download.svg'>Download Binding cover sheet for locality %LOKALITA%</a></li></ul></div>",
        ],
    },

    // identify result tabs (tab titles and services on tab)
    tabs: [
        {
            title: "Lokality MPP",
            display: "lokality",
            tableHeader: [],
        },
        /* {
			"title": "Transformační a rozvojové plochy",
			"display": "transf_uzemi",
			"tableHeader": []
		}, */
        {
            title: "Dokumenty ke stažení",
            display: "lokality_kl",
            tableHeader: [],
        },
    ],

    resultClassName: "identify-result",
}
