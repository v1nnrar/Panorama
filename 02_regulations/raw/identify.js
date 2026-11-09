function Identify (view, config) {

	this.view = view;
	this.config = config;

	this.tasks = null;
	this.iPars = null;
	this.all = null;
	this.progressIndicator = null;
	this._graphicsLayer = undefined;
	this._graphics = {};
	this._symbols = {};
	this.sourceUrls = []
	this.lokalitaInfo = {}
	this.queryUrl = "https://services5.arcgis.com/SBTXIEUGWbqzUecw/arcgis/rest/services/mpp_info/FeatureServer/2"

	this._tabsId = "identify-results-tabs";
	//var _this = this;
	//var onChangeFn = function(id) { _this.resultTabChange(id); };
	
	this.resultTabs = new Tabs(this._tabsId);
	this._translations = {}
	//this.resultTabs.onChange(onChangeFn);

	require([
		"esri/rest/support/IdentifyParameters",
		"esri/layers/GraphicsLayer",
		"dojo/_base/lang",
		"dojo/_base/connect",
		"privateModules/ProgressIndicator",
		'modules/Utils'
	], (
		IdentifyParameters,
		GraphicsLayer,
		lang,
		connect,
		ProgressIndicator,
		Utils
	) => {

		if (Utils.getTranslations()) {
			const searchTranslations = Utils.getTranslations().Search.MPPLocality;
			const identifyTranslations = Utils.getTranslations().Identify;
			this._translations = Object.assign(searchTranslations, identifyTranslations);
		} else {
			this._translations = undefined;
		}

		this._languageIndex = Utils.getLanguageIndex();

		this._clickPoint = {}

		const uniqueSourceIds = [...new Set(this.config.sourceIds)]

		uniqueSourceIds.map ((sourceId) => {

			const url = Utils.getSourceUrl(sourceId.split("/")[0]);
			this.sourceUrls.push(url + "/" + sourceId.split("/")[1])
		});
		

		// create graphics layer to display found graphics
        var params = { 
            id: 'identifyResults',
            listMode: "hide"
        };
        this._graphicsLayer = new GraphicsLayer(params);

        app.map.add(this._graphicsLayer);

        this.view.popup.watch("visible", (newValue, oldValue) => {
		    if (newValue == false && oldValue != null) {
				this._graphicsLayer.removeAll();
		    } else if (newValue == true) {
		    	var node = $( '#' + this._tabsId );
		    	if (node) {
		            node.tabs({
		            	activate: (e, ui) => {
		            		this.resultTabChange($( '#' + this._tabsId ).tabs("option", "active"));
		            	}
		            });
		    	}
		        this.connectGraphics();
		    }
		});

        /* this._symbols = {
			point0: {
				type: "simple-marker",
				style: "circle",
				color: [255, 0, 0],
				size: 8,
				outline: {
					color: [255, 0, 0],
					width: 1
				}
			},
			point1: {
				type: "simple-marker",
				style: "circle",
				color: [238, 238, 102],
				size: 8,
				outline: {
					color: [238, 238, 102],
					width: 1
				}
			},
			polyline0: {
				type: "simple-line",
				color: [255, 0, 0],
				color: [255, 0, 0],
				width: 3
			},
			polylineline1: {
				type: "simple-line",
				color: [238, 238, 102],
				width: 3
			},
			polygon0: {
				type: "simple-fill",
				style: "backward-diagonal",
				color: [0, 0, 0],
				outline: {
					color: [255, 0, 0],
					width: 2
				}
			},
			polygon1: {
				type: "simple-fill",
				style: "solid",
				color: [238, 238, 102, 0.2],
				outline: {
					color: [238, 238, 102],
					width: 2
				}
			},
			polygon2: {
				type: "simple-fill",
				style: "solid",
				color: [0, 0, 0],
				outline: {
					color: [255, 0, 0],
					width: 2
				}
			}
		} */
		const fillSymbol = {
			type: "simple-fill",
			color: [200,0,0,0.2],
			outline: {
				color: [200,0,0,1],
				width: 1
			}
		}
		// create symbols for highlight graphics
		const fillHighlightSymbol = {
			type: "simple-fill",
			color: [0,255,255,0.2],
			outline: {
				color: [0,255,255,1],
				width: 2
			}
		}

		this._symbols = {
			default: fillSymbol,
			highlight: fillHighlightSymbol
		};

		// create identify parameters
		this.iPars = new IdentifyParameters();
		this.iPars.layerOption = "all";

		var mapElId = this.view.container.id;
		var params = { targetElementId: mapElId };
		// create progress indicator
		this.progressIndicator = new ProgressIndicator(params);
		this.progressIndicator.init();


		// handle when other actions block or unblock map click
		this.isActive = true;
		 
		connect.subscribe("rightClickOnMapEventBlocked", lang.hitch(this, "deactivate"));
		connect.subscribe("rightClickOnMapEventUnblocked", lang.hitch(this, "activate"));

	});

	// add map left click handler
	this.view.on("click", $.proxy(this.onMapClick, this));
}

Identify.prototype.activate = function (arguments) {

	this.isActive = true;

};

Identify.prototype.deactivate = function (arguments) {

	this.isActive = false;

};

Identify.prototype.onMapClick = function (evt) {
	if ((evt.which == 1) || (evt.button == 0)) {
		var measureModule = app.modules["privateModules/MeasureWidget"];
		if (this.isActive == false || measureModule.active == true) { return; }
	
		var pars = this.setPars(evt.mapPoint);
		var tasks = this.setTasks(pars);
		//var callback = $.proxy(this.mapClickRes, this);
		this._clickPoint = {x: evt.x, y: evt.y};
		this._graphicsLayer.removeAll();
		this.progressIndicator.show("Zjišťuji informace...");

		Promise.all(tasks)
			.then((results) => {
				this.mapClickRes(results)
			})
			.catch(err => {
				this.progressIndicator.hide();
				console.log(err)
				alert("Ve vyhledávání nastala chyba.");
			})
		//this.promise(tasks, callback);
	
	}
};

// set identify parameters
Identify.prototype.setPars = function (mapPoint) {

	var pars = this.iPars;
	pars.tolerance = 0;
	pars.returnGeometry = true;
	pars.width = this.view.width;
	pars.height = this.view.height;
	pars.geometry = mapPoint;
	pars.mapExtent = this.view.extent;

	return pars;

};

// set identify tasks
Identify.prototype.setTasks = function (identifyPars) {
	const tasks = [];

	require(["esri/rest/identify"], (identify) => {
	
		this.sourceUrls.forEach(url => {
			tasks.push(identify.identify(url, identifyPars));
		})
	
	})
	return tasks;		

}

// add promises on tasks
Identify.prototype.promise = function (tasks, callback) {

	require(["dojo/promise/all"],
	$.proxy(function (all) {

		// wait until all tasks are completed
		var promises = new all(tasks);
		promises.then(callback);

	}, this));

};

// get map click results
Identify.prototype.mapClickRes = function (res) {

	if (window.matchMedia("(max-width: 1024px)").matches) {
		const lokalitaExtent = res[0].results[0].feature.geometry.extent
		lokalitaExtent.xmin = lokalitaExtent.xmin - 100
		lokalitaExtent.xmax = lokalitaExtent.xmax + 100
		lokalitaExtent.ymin = lokalitaExtent.ymin - 100
		lokalitaExtent.ymax = lokalitaExtent.ymax + 100
		app.view.extent = lokalitaExtent
	}

	require(["esri/rest/query", "esri/rest/support/Query"], (query, Query) => {
		const lokalita = res[0].results[0].feature.attributes["LOKALITA"]


		const queryObj = new Query()
		queryObj.where = "LOKALITA = '" + lokalita + "'"
		queryObj.outFields = ["*"]
		queryObj.returnGeometry = false

		query.executeQueryJSON(this.queryUrl, queryObj)
			.then(response => {
				const cilovyCharakter = response.features
				this.progressIndicator.hide();
				this._graphicsLayer.removeAll();
			
				this.results = this.parseResults(res, cilovyCharakter);
			
				// display popup window
				var title = "informace o objektech";
				var mapPoint = this.iPars.geometry;
			
				this.dispPopup(title, "", mapPoint, this.results);
				this.dispGraphics(this.results)
				//this.createTabs(this.results);
			
				// display tab features in map
				this.resultTabChange(this.resultTabs.selectedItem);
			})
	})

	// connect graphics to res
	//this.connectGraphics();

};


// parse click results to internal results structure
Identify.prototype.parseResults = function (results, cilovyCharakter) {

	var tabs = [];
	var tabsTemplate = this.config.tabs;

	tabsTemplate.map((tab) => {

		var tabTitle = (tab.title.substring(0,5) == "dict_") ? this.getTranslation(tab.title) : tab.title;

		var tableHeader = [];
		if (tab.tableHeader) {
			tab.tableHeader.forEach(function(item, index) {
				tableHeader[index] = (item.substring(0,5) == "dict_") ? this.getTranslation(item) : item;
			});		
		}

		tabs.push({
			title: tabTitle,
			tableHeader: tableHeader,
			results: this.tabResults(results, tab.display, cilovyCharakter)
		});

	});

	return tabs;

};

// parse one result to internal structure
Identify.prototype.parseResult = function (result, templateIdx, serviceId, cilovyCharakter) {

	var template = this.config.templates[templateIdx];
	var feature = result.feature;
	var layerId = result.layerId;
	var attributes = feature.attributes;
	var resultId = templateIdx.toString() + layerId.toString() + attributes.OBJECTID;
	let htmlStr = ""
	if (template[layerId]) {
		htmlStr = this.templateToHtml(template[layerId], attributes, serviceId, cilovyCharakter);
	} else if (!template[layerId] && serviceId == "transf_uzemi") { 
		htmlStr = "V místě se nenachází žádná transformační nebo rozvojová plocha."
	}

	// unique identifier of the result
	attributes._resultId_ = resultId;

	return {
		resultId: resultId,
		resultCls: this.config.resultClassName,
		htmlStr: htmlStr,
		feature: feature
	};

};

// return results for one tab
Identify.prototype.tabResults = function (results, serviceIds, cilovyCharakter) {

	var res = [];
	var indexes = this.config.indexes;

	serviceIds.map((id) => {
		var idx = indexes[id];
		//!!!!len ak všetky info sú ťahané z jednej služby!!!!
		var serviceResults = results[0].results;

		serviceResults.map((result) => {

			var result = this.parseResult(result, idx, id, cilovyCharakter);
			if (result && result.htmlStr) { res.push(result); }

		});

	});

	return res;
	
};

// when results tab is changed by user
Identify.prototype.resultTabChange = function (tabId) {

	//this._graphicsLayer.removeAll();

	this._graphicsLayer.graphics.forEach(graphic => {
		this.setSymbol(graphic, false);
	})

	var results = this.results[tabId].results;

	results.map((result) => {
		// don't show graphics for whole Prague elements
		/* if (result.feature.attributes["SHAPE.AREA"] && parseInt(result.feature.attributes["SHAPE.AREA"]) > 496166000) {
			return;
		} else {
			this.addGraphic(result.feature);
		} */
		const graphic = this._graphicsLayer.graphics.find(item => {
			return item.id == "graphic_" + tabId
		})
		this.setSymbol(graphic, true);
		this._graphicsLayer.graphics.reorder(graphic, this._graphicsLayer.graphics.items.length);
	});

};

// display map info window
Identify.prototype.dispPopup = function (title, content, mapPoint, results) {

	this.view.popup.title =  title;

	var nodesStr = this.resultTabs.nodesStr(this._tabsId, results);
	this.view.popup.content = nodesStr;
	this.view.popup.collapseEnabled = false;
	this.view.popup.dockOptions.buttonEnabled = false;
	this.view.popup.alignment = "top-center";
	this.view.popup.actions = [];
	//this.view.popup.resize(610, 400);

	if (window.matchMedia("(max-width: 1024px)").matches) {
		this.view.popup.dockEnabled = true
	} else {
		if (this.view.width - this._clickPoint.x < 265 || this._clickPoint.x - 265 < 0 || this._clickPoint.y - 300 < 0) {
			this.view.goTo(mapPoint, {duration: 750});
		} 
	}
	this.view.popup.open({
		location: mapPoint
	});

};

Identify.prototype.dispGraphics = function (results) {
	results.forEach((res, i) => {
		if (res.results.length > 0) {
			this.addGraphic(res.results[0].feature, i);
		}
	})
};

// add feature to map
Identify.prototype.addGraphic = function (feature, index) {

	require(["esri/Graphic"], (Graphic) => {
		
		var graphic = new Graphic({
			geometry: feature.geometry,
			attributes: feature.attributes,
			id: "graphic_" + index
		});
		this._graphicsLayer.add(graphic);
		this.setSymbol(graphic);	
	});

};

// change feature symbol when user move over a result raw
Identify.prototype.connectGraphics = function () {
	
	var clsName = this.config.resultClassName;

	$( '.' + clsName ).on("mouseenter", () => {

		var featureId = $(this).attr("id").replace(clsName, "");
		var feature = this.featureByAttr("_resultId_", featureId);

		if (!feature) { return; }

		this.setSymbol(feature, true);
		this._graphicsLayer.graphics.reorder(feature, this._graphicsLayer.graphics.items.length);

	});

	$( '.' + clsName ).on("mouseleave", () => {
			
		var featureId = $(this).attr("id").replace(clsName, "");
		var feature = this.featureByAttr("_resultId_", featureId);

		if (!feature) { return; }

		this.setSymbol(feature);

	});

};

// set appropriate symbol to feature
Identify.prototype.setSymbol = function (feature, highlight) {
	
	//var symId = this.getSymbolId(feature, highlight);
	if (highlight) {
		feature.symbol = this._symbols["highlight"];
	} else {
		feature.symbol = this._symbols["default"];
	}
		

};

// return appropriate symbol ID for a feature
Identify.prototype.getSymbolId = function (feature, highlight) {

	var geomType = feature.geometry.type;
	var highlight = highlight ? 1 : 0;
	var type = geomType + highlight;

	if (!highlight &&
		((feature.attributes._resultId_ === "312036") ||
		(feature.attributes._resultId_ === "312037"))) {
		type = "polygon2";
	}

	return type;

};

// return graphicsLayer features filtered by a specified attribute
Identify.prototype.featureByAttr = function (attrName, value) {
	
	var graphics = this._graphicsLayer.graphics;

	return graphics.find(function (graphic) {
		return graphic.attributes[attrName] === value;
	});

};

// create html string from feature attribute template
Identify.prototype.templateToHtml = function (template, attrs, serviceId, cilovyCharakter) {

	const indRegulativy = {}
	cilovyCharakter.forEach(item => {
		indRegulativy[item.attributes["KAPITOLA"]] = item.attributes
	})

	if (!template && serviceId == "transf_uzemi") { 
		return "V místě se nenachází žádná transformační nebo rozvojová plocha."
	}
	
	template = (template.substring(0,5) == "dict_") ? this.getTranslation(template) : template;

	var html = "";
	var split = template.split("%");

	if (split.length < 3) {
		return template;
	}

	for (var i = 0; i < split.length; i += 2) {
		
		html += split[i];
		
		var attrVal = split[i + 1];

		if (attrVal) {

			if (attrVal === "VYMERA" && split[i] != "&area=") {
				html += (parseFloat(attrs[attrVal]) / 10000).toFixed(3) + " ha";
			}
			else if (attrVal === "GETPODNET") {
				var val1 = attrs["CISLO_TXT"];
				var val2 = attrs["PUP_CUR.PUP_PODNETY_VSE_P.CISLO_TXT_2"];
				var typUpd = attrs["TYP_UPD"];

				if (val2 !== "Null") {
					html += val2 + "+" + typUpd + "+[" + val1 + "]";
				}
				else {
					html += val1 + "+" + typUpd;
				}

			}
			else if (attrVal === "SHAPE.AREA") {
				if (parseInt(attrs["SHAPE.AREA"]) > 496166000) {
					html += " - území celé Prahy";
				}/*  else {
					html += attrs[attrVal];
				} */
			}
			else if (attrVal.split("|").length === 2) {
				var attr1 = attrVal.split("|")[0];
				var attr2 = attrVal.split("|")[1];
				var val1 = attrs[attr1];
				var val2 = attrs[attr2];

				if (val1 === "Null" && val2 !== "Null") {
					html += val2;
				}
				else if (val1 !== "Null" && val2 === "Null") {
					html += val1;
				}
				else if (val1 !== "Null" && val2 !== "Null") {
					html += val1 + " (" + val2 + ")";
				}
				else {
					html += "";
				}
				
			}
			else {
				html += attrs[attrVal];
			}

		}

	}

	if (serviceId == "lokality") {
		html += `
			<li class="infoPopupItemTitle">
				<b>${attrs["LOKALITA"]} / ${attrs["NAZEV"]}</b>
			</li>
			<li>
				${this._getTranslation("dict_zastavitelnost")}${this._getTranslation("dict_zastavitelnost_" + attrs["ZASTAVITELNOST"])}
			</li>
			<li>
				TYP STRUKTURY: ${attrs["STRUKTURA_TXT"]}
			</li>
			<li>
				ZPŮSOB VYUŽITÍ: ${attrs["VYUZITI_TXT"]}
			</li>
			<li>
				MÍRA STABILITY: ${attrs["STABILITA_TXT"]}
			</li>
		`
		const zastavitelnost = attrs["ZASTAVITELNOST"]
		const regulativyEnum = {
			1000: [100, zastavitelnost < 3 ? "MĚSTSKÁ PŘÍRODA" : "OTEVŘENÁ KRAJINA" ],
			2000: [200, "VYSTAVĚNÉ PROSTŘEDÍ" ],
			3000: [300, "VYUŽITÍ ÚZEMÍ" ],
			4000: [400, "STABILITA A MÍRA VYUŽITÍ ÚZEMÍ" ],
			5000: [500, "KRAJINNÁ INFRASTRUKTURA" ],
			6000: [600, "DOPRAVNÍ INFRASTRUKTURA" ],
			7000: [700, "TECHNICKÁ INFRASTRUKTURA" ],
			8000: [800, "VEŘEJNÁ VYBAVENOST" ],
			9000: [900, "VEŘEJNÝ ZÁJEM" ],
		}

		html += `
		<li class="infoPopupItemSubtitle">
			<b>CÍLOVÝ CHARAKTER LOKALITY</b>
		</li>
		<li>
			${indRegulativy["0"]["PEREX"]} Lokalita je součástí krajiny vymezené v ZÚR s názvem ${attrs["KRAJINA_ZUR_TXT"]}.
		</li>
		<li>
			${indRegulativy["0"]["TXTSTAV"]}
		`
		for (let item in regulativyEnum) {
			const reg = regulativyEnum[item]
			html += `
			<li class="infoPopupItemSubtitle">
				<b>${reg[0]} / ${reg[1]}</b>
			</li>
			`
			if (indRegulativy[item]) {
				html += `<li>${indRegulativy[item]["TXTSTAV"]}</li>`
			} else {
				html += "Individuální regulativy nejsou stanoveny."
			}
		}

		html += "</ul></div></div>"
	}

	if (serviceId == "transf_uzemi") {
		if (attrs["SKUPINA"]) {
			const cleneni = attrs["CLENENI_UZEMI"] == 1 ? "zastavitelných" : attrs["CLENENI_UZEMI"] == 2 ? "nestavebních" : "nezastavitelných"
			html += `
				<li>
					${attrs["KOD_SKUPINA"]}
				</li>
				<li>
					Skupina ${cleneni} [T+R] ploch složená z celkem ${attrs["POCETPLOCH"]} vzájemně sousedících transformačních a rozvojových ploch o souhrnné rozloze ${formatThousands(attrs["ROZLOHA"])} m<sup>2</sup>
				</li>
			`
		} else {
			const stabilita = (attrs["IDTXT_LIST"].includes("T")) ? "transformační" : "rozvojová"
			html += `
				<li>
					${attrs["RT_PRVKY"]}
				</li>
				<li>
					${attrs["CLENENI_UZEMI_TXT"]} ${stabilita} plocha o rozloze ${formatThousands(attrs["ROZLOHA"])} m<sup>2</sup>
				</li>
			`
		}

		if (attrs["MIRA_VYUZITI"]) {
			html += `
				<li>
					Míra využití: ${attrs["MIRA_VYUZITI_TXT"]}
				</li>
			`
		}
		// Zastavitelné malé rozvojové plochy navazující na stávající strukturu
		if (attrs["CLENENI_UZEMI"] == 1 && attrs["MIRA_VYUZITI"] == 1) {
			html += typStrukturyZpusbVyuziti(attrs)
		}
		// Zastavitelné transformační a rozvojové plochy doplňující stávající struktury
		if (attrs["CLENENI_UZEMI"] == 1 && attrs["MIRA_VYUZITI"] == 2) {
			html += typStrukturyZpusbVyuziti(attrs)
			if (attrs["PODIL_ZB_M"]) {
				html += koeficientZastaveniStavebnihoBloku(attrs)
			} else {
				if (attrs["PODIL_Z_PLOCHA"]) {
					html += `
						<li>
							Zastavitelnost z velikosti plochy: ${attrs["PODIL_Z_PLOCHA"]} % 
						</li>
					`
				} else {
					html += `
						<li>
							Zastavitelnost z velikosti plochy: nestanovuje se 
						</li>
					`
				}
			}
			html += pozadavekNaUmisteni(attrs)
			
		}
		// Zastavitelné transformační a rozvojové plochy nových struktur
		if (attrs["CLENENI_UZEMI"] == 1 && attrs["MIRA_VYUZITI"] == 3) {
			html += typStrukturyZpusbVyuziti(attrs)
			html += minMaxpodily(attrs)
			html += koeficientZastaveniStavebnihoBloku(attrs)
			html += pozadavekNaUmisteni(attrs)
		}
		// Nestavební transformační a rozvojové plochy || Nezastavitelné transformační a rozvojové plochy
		if (attrs["CLENENI_UZEMI"] == 2 || attrs["CLENENI_UZEMI"] == 3) {
			html += `
				<li>
					Způsob využití: ${attrs["VYUZITI_TXT"]}
				</li>
			`
			html += cilovaCharakteristikaPlochy(attrs)
		}

		if (attrs["INDIVIDUALNI_REG"]) {
			html += `
				<li>
					${attrs["INDIVIDUALNI_REG"]}
				</li>
			`
		}

		html += "</ul></div></div>"

	}

	return html;

};
function typStrukturyZpusbVyuziti(attrs) {
	return `
		<li>
			Typ struktury: ${attrs["STRUKTURA_TXT"]}
		</li>
		<li>
			Způsob využití: ${attrs["VYUZITI_TXT"]}
		</li>
	`
}

function koeficientZastaveniStavebnihoBloku(attrs) {
	//const zbs = attrs["PODIL_ZB_V"] + (attrs["PODIL_ZB_S1"] - attrs["PODIL_ZB_V"]) * (12000 - attrs["ROZLOHA"]) / 10000
	return `
		<li>
			Koeficient zastavění stavebního bloku ZB:
		</li>
		<li>
			ZB<sub>M</sub>: ${attrs["PODIL_ZB_M"]} % (pro malé bloky do 2 000 m<sup>2</sup>)
		</li>
		<li>
			ZB<sub>S1</sub>: ${attrs["PODIL_ZB_S1"]} %
		</li>
		<li>
			ZB<sub>S</sub>: [ZB<sub>V</sub> + (ZB<sub>S1</sub> - ZB<sub>V</sub>) × (12 000 - plocha bloku) / 10 000] (pro střední bloky od 2 001 m<sup>2</sup> do 12 000 m<sup>2</sup>)
		</li>
		<li>
			ZB<sub>V</sub>: ${attrs["PODIL_ZB_V"]} % (pro velké bloky nad 12 000 m<sup>2</sup>)
		</li>
		<li>
			ZB<sub>N</sub>: ${attrs["PODIL_ZB_N"]} % (pro neznámý blok)
		</li>
	`
}

function pozadavekNaUmisteni(attrs) {
	let html = ""
	if (!attrs["SKUPINA"]) {
				
		if (attrs["PARKY_POCET"]) {
			html += `
				<li>
					V ploše je bodem vyjádřen požadavek na umístění parku.
				</li>
			`
		}
		if (attrs["NAMESTI_POCET"]) {
			html += `
				<li>
					V ploše je bodem vyjádřen požadavek na umístění náměstí.
				</li>
			`
		}
		if (attrs["VYBAVENOST_POCET"]) {
			html += `
				<li>
					V ploše je bodem vyjádřen požadavek na umístění veřejné vybavenosti.
				</li>
			`
		}
	} else {
		if (attrs["PARKY_POCET"]) {
			html += `
				<li>
					Ve skupině [T+R] ploch je bodem vyjádřen požadavek na umístění parku.
				</li>
			`
		}
		if (attrs["NAMESTI_POCET"]) {
			html += `
				<li>
					Ve skupině [T+R] ploch je bodem vyjádřen požadavek na umístění náměstí.
				</li>
			`
		}
		if (attrs["VYBAVENOST_POCET"]) {
			html += `
				<li>
					Ve skupině [T+R] ploch je bodem vyjádřen požadavek na umístění veřejné vybavenosti.
				</li>
			`
		}
	}
	return html
}

function minMaxpodily(attrs) {
	let html = ""
	html += `
		<li>
			Minimální podíl uličních prostranství UP<sub>min</sub>: ${attrs["PODIL_UP_MIN"]} %
		</li>
		<li>
			Minimální podíl městských parků PP<sub>min</sub>: ${attrs["PODIL_UP_MIN"]} %
		</li>
	`
	if (attrs["PODIL_VP_MAX"]) {
		html += `
			<li>
				Maximální podíl veřejných prostranství VP<sub>max</sub>: ${attrs["PODIL_VP_MAX"]} %
			</li>
		`
	} else {
		html += `
			<li>
				Maximální podíl veřejných prostranství VP<sub>max</sub>: nestanovuje se
			</li>
		`
	}
	html += `
		<li>
			Minimální podíl občanské vybavenosti OV<sub>min</sub>: ${attrs["PODIL_OV_MIN"]} %
		</li>
	`
	return html
}

function cilovaCharakteristikaPlochy(attrs) {
	let html = ""
	if (attrs["CIL_CHAR_PLOCHY"]) {
		if (!attrs["SKUPINA"]) {
			html += `
				<li>
					Cílová charakteristika plochy: ${attrs["CIL_CHAR_PLOCHY_TXT"]}
				</li>
			`
		} else {
			html += `
				<li>
				Cílová charakteristika skupiny [T+R] ploch: ${attrs["CIL_CHAR_PLOCHY_TXT"]}
				</li>
			`
		}
	}
	return html
}

function formatThousands(val) {
	return val.toString().replace(/(\d|\uE000)(?=(\d{3}|\d{3}\uE000|\d\uE000\d{2}|\d{2}\uE000\d|\uE000\d{3}|\d\uE000\d\uE000\d|\uE000\d\uE000r\d\uE000\d|\d\uE000\d\uE000\d\uE000)+(?!(\d|\uE000\d|\d\uE000)))/g, "$1"+"\u202F")
}

function _getTranslation(key) {

	const langIndex = Utils.getLanguageIndex();
	return this._translations[key][langIndex];
}

function getLanguageIndex () {
	const langIndex = (app.languageIndex) ? app.languageIndex : 0;
	return langIndex;
}