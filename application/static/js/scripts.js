// scripts.js – Software ACUITEE
// Copyright 2021 b<>com. All rights reserved.
// This software is licensed under the Apache License, Version 2.0.
// You may not use this file except in compliance with the license. 
// You may obtain a copy of the license at: 
// http://www.apache.org/licenses/LICENSE-2.0 
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, 
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and 
// limitations under the License.

$(document).ready(onload());

function onload() {
	$(document).ajaxStop($.unblockUI);	
	$("#ParsedNoteID").hide();
	formControl();	
}

function InitializeNoteTextarea() {	
	var example = "Chère Consœur,\n" +
	"Je vous remercie de m'avoir adressé en consultation de génétique la jeune PRENOM NOM, née le DD/DD/DDDD, accompagnée de ses parents. PRENOM est suivie pour un retard global de développement associé à des difficultés de comportement.\n" +
	"Sur le plan familial, PRENOM est le seul enfant du couple. La maman a eu d'une première union un fils âgé de 10 ans en bonne santé et qui n'a pas eu de problème dans son développement. Les parents ne sont pas apparentés. Le papa est en parfaite santé. A noter chez son neveu un trouble du spectre de l’autisme avec un suivi au CAMSP. La maman est en bonne santé et il n'existe pas d'antécédent notable de son côté.\n" +
	"Concernant PRENOM, la grossesse avait été marquée par une clarté nucale augmentée, sans autre anomalie lors du suivi échographique. Elle est née à terme avec des mensurations dans la norme.\n" +
	"Sur le plan développemental, il existe un retard psychomoteur avec une tenue assise acquise à l'âge de 15 mois, une marche acquise à l'âge de 3 ans ayant nécessité une prise en charge en kinésithérapie. Sur le plan du langage, elle est actuellement capable de répéter quelques mots mais ne construit pas actuellement de phrases. Sur le plan du comportement, elle se montre assez hyperactive, avec des difficultés attentionnelles. Elle n'a jamais fait de crise d'épilepsie. \n" +
	"A l'examen ce jour, à l'âge de 4 ans, PRENOM pèse 12 kg, inférieur à - 2 DS pour une taille de 99 cm (-1 DS) et un PC mesuré à 46.5 cm (-2.5 DS). Il existe une hyperlaxité distale. Sur le plan cardiaque, je n'ai pas perçu de souffle. On note sur le plan morphologique quelques particularités, à savoir des oreilles basses et en rotation postérieure, un épicanthus, une racine du nez assez proéminente. \n" +
	"Au total, je rencontre ce jour PRENOM âgé de 4 ans qui présente un retard global de développement associé à des troubles comportementaux et une microcéphalie. Devant ce tableau, je n'ai pas de diagnostic étiologique précis et propose la réalisation d'un exome en trio. Les deux parents ont donc été prélevés ce jour pour réaliser cette analyse. \n" +
	"Je ne manquerai pas de tenir informé la famille dès réception des résultats.\n" +
	"Confraternellement. ";
	document.getElementById("noteTextarea").value = example;
}

function Parse() {	
	var Parser_StrMatch_Element = document.getElementById("Parser_StrMatch");
	var Parser_ENLIGHTOR_Element  = document.getElementById("Parser_ENLIGHTOR");
	var bParser_StrMatch=Parser_StrMatch_Element.checked
	var bParser_ENLIGHTOR=Parser_ENLIGHTOR_Element.checked

	var note = $("#noteTextarea").val();
	$("#id_ParsedNote").text(note);
	var formData = {
		'note' : note,
		'bStrMatch': bParser_StrMatch,
		'bENLIGHTOR': bParser_ENLIGHTOR
	};
	$.blockUI({ message: '<h6> The note is being parsed. Please wait! </h6>' });

	$.ajax({
			headers : {
				'Accept' : 'application/json',
				'Content-Type' : 'application/json'
			},
			type : 'POST',
			url : "parse/bcom",
			data : JSON.stringify(formData),
			dataType : "json",
			success : function(terms) {			
				createParsedNoteHtml(terms);
				updateResultsTable(terms);
			},
			error : function(XMLHttpRequest, textStatus, errorThrown) {
				console.log("Parse() problem!");				
			}
		});
}

function Savejson() {	
	var resRaw = get_annotation_results();
	var res = prepareOutputJson(resRaw);
	$.blockUI({ message: '<h6> The note is being saved. Please wait! </h6>' });
	$.ajax({
			headers : {
				'Accept' : 'application/json',
				'Content-Type' : 'application/json'
			},
			type : 'POST',
			url : "savejson",
			data : JSON.stringify(res),
			dataType : "json",
			success : function(terms) {			
				console.log("Json saved");
			},
			error : function(XMLHttpRequest, textStatus, errorThrown) {
				console.log("Savejson() problem!");				
			}
		});
}

function Reset_Annotated_Phrase_Panel(){
	show_HPO_Term_Details_Table(null);
	Init_Search_Results_Table();
	$("#SelectedEntityInfo").attr('lastElementID',"None");
	document.getElementById("SelectedEntityInfo").innerHTML = "Please select an entity to show/edit the annotation details";
}

function formControl() {
	//InitializeNoteTextarea();	
	$("#buttonParse").on("click", function() {
		Parse();
		$("#NoteTextID").hide();
		$("#id_Parsed_Div").show();
		
	});	

	$("#buttonSave").on("click", function() {
		Savejson();
	});

	$("#buttonNewNote").on("click", function() {
			$("#NoteTextID").show();
			$("#id_Parsed_Div").hide();			
			Reset_Annotated_Phrase_Panel();
	});

	$("#buttonValidate").on("click", function() {
		validate();			
		});
	
	$("#buttonRemoveUnit").on("click", function() {
		RemoveAnnotationUnit();			
		});		
	
	$(document).keypress(function (e) {
		if (e.keyCode === 13) {			
			$("#insertTermMouseEnter").click();
		}
	});
	$("#searchAddHPO").on("keyup", function() {
		var value = $(this).val().toLowerCase();
		if(value.length>3){
			search_HPO_Terms(value);
		}
		else{
			Reset_Search_Results_Table();
		}
	  });
	$("#buttonExport").on("click", function() {
			var resRaw = get_annotation_results();
			var res = prepareOutputJson(resRaw);
			var resStr=JSON.stringify(res);
			$(
					"<a />",
					{
						"download" : "data.json",
						"href" : "data:application/json,"
							 + encodeURIComponent(resStr)
					}).appendTo("body").click(function() {
				$(this).remove()
			})[0].click()
		});
}

function prepareOutputJson(resJson_raw){
	resJson=resJson_raw
	//alert(typeof resJson_raw)
	//const resJson = (({ start, length, negated ,concerned_person,mult_CS, hpoAnnotation}) => ({ start, length, negated ,concerned_person,mult_CS, hpoAnnotation}))(resJson_raw);

	//var resJson = resJson_raw.pick( ['start', 'length','negated' ,'concerned_person','mult_CS', 'hpoAnnotation']); 
	//alert(JSON.stringify(resJson))

	for (key in resJson) {
		if (resJson.hasOwnProperty(key)) {
			delete resJson[key].validated;			
			//convert the concerned_person from index to name for readability
			var concerned_person= parseInt(resJson[key].concerned_person);
			switch (concerned_person) {
				case -1: { // Patient 1
					resJson[key].concerned_person='Not defined';
					break;
				}
				case 0: { // Patient 1
					resJson[key].concerned_person='Patient';
					break;
				}
				case 1: { // Parental line
					resJson[key].concerned_person='Parental line';
					break;
				}
				case 2: { // Maternal line
					resJson[key].concerned_person='Maternal line';
					break;
				}
				case 3: { // Patient 2
					resJson[key].concerned_person='Patient 2';
					break;
				}
				case 4: { // Other
					resJson[key].concerned_person='Other';
					break;
				}
			}			
		}
	}
	// delete the annotation unit if no hpo terms are found
	let i = resJson.length;
	while (i--) {
		if (resJson[i].hpoAnnotation.length==0){
			resJson.splice(i, 1);
		}
	}
	// Reorder the object keys : ['start', 'length','negated' ,'concerned_person','mult_CS', 'hpoAnnotation']
	var resJson_ordered = [];
	for (let i = 0; i< resJson.length; i++) {
		dictTemp={
			"start": resJson[i].start,
			"length": resJson[i].length,
			"sentence" : resJson[i].sentence,
			"negated" : resJson[i].negated,
			"concerned_person" :	resJson[i].concerned_person,
			"mult_CS" :resJson[i].mult_CS,
			"hpoAnnotation" : resJson[i].hpoAnnotation			
		};
		resJson_ordered.push(dictTemp);
	}
	// Add the annotator name and the annotation date 
	annotator_ID=get_annotator_ID()
	source_ID=get_source_ID()
	const annotation_Date = new Date();	
	annotation_Date_str=annotation_Date.toLocaleDateString("fr-FR");
	return {"date":annotation_Date_str,"annotator_ID":annotator_ID,"source_ID":source_ID,"annotations":resJson_ordered};
}

function Export_Results_Json(){
	alert("Export results here")
}

function search_HPO_Terms(query){	
	var formData = {
		'query' : query		
	};
	$.ajax({
			headers : {
				'Accept' : 'application/json',
				'Content-Type' : 'application/json'
			},
			type : 'POST',
			url : "Search_Terms",
			data : JSON.stringify(formData),
			dataType : "json",
			success : function(matched_terms) {
				Fill_Search_Results_Table(matched_terms);
			},
			error : function(XMLHttpRequest, textStatus, errorThrown) {
				console.log("search_HPO_Terms() problem!");
			}
		});
}

function Init_Search_Results_Table(){
	document.getElementById('searchAddHPO').value = "";
	Fill_Search_Results_Table([]);
}
function Reset_Search_Results_Table(){
	Fill_Search_Results_Table([]);		
}

function Fill_Search_Results_Table(terms){

	var json_terms = [];
	for (let i = 0; i< terms.length; i++) {
		hpoId=terms[i]['ID'];
		hpoTerm=terms[i]['term'];		
		
		var spanClass="button-add-term";
		spanID=hpoId+"_"+i;
		//spanID_href = '<a href="javascript:show_HPO_term_details(\''+hpoId+'\');">'+spanID+'</a>';
		var strStart='<span onclick="add_HPO_Term(this)"'+
			'class= "'+spanClass+'"'+					
			' id= ' + spanID + '>';
		var strEnd='<i class="fas fa-plus"></i></span>';
		var ActionStr=	strStart+strEnd;
		strStart='<span onclick="(this)"'+
			'class= "'+spanClass+'"'+					
			' id= ' + hpoId + '>';
		strEnd='<i class="fas fa-info"></i></span>';
		ActionStr=	ActionStr+strStart+strEnd;
		
		dictTemp={
			"ID": spanID,
			"Term": hpoTerm,
			"Actions" : ActionStr			
		};
		json_terms.push(dictTemp);
	}

	var table = $('#searchResultsTable').DataTable(
	{
		"data" : json_terms,
		"columns" : [
				{
					"data" : "ID"
				},
				{
					"data" : "Term"
				},
				{
					"data" : "Actions"
				}				
		],
		autoWidth: true,
		responsive : true,
		lengthChange : false,
		buttons : [ 'excel', 'pdf' ],
		searching : false,
		paging : false,
		info : false,
		showHeader: false,
		"bDestroy" : true
	});
	
}

function info_HPO_Term(infoUnit){
	ctrlID=infoUnit.id;
	var id_segments = ctrlID.split("_"); // HpoID_ParserID
	var hpoId = id_segments[0];
	var parserID = id_segments[1];
	show_HPO_term_details(hpoId,parserID);
}

function add_HPO_Term(term){
	ctrlID=term.id;
	var id_segments = ctrlID.split("_"); // HpoID_rowIndex
	var hpoId = id_segments[0];	
	var hpoTerm =""
	// read the hpoTerm from the datatable of serach results 
	var resTab = document.getElementById('searchResultsTable');
	for (i = 1; i < resTab.rows.length; i++) {
		var objCells = resTab.rows.item(i).cells;
		if(objCells.item(0).innerHTML==ctrlID){
			hpoTerm=objCells.item(1).innerHTML;
			break;
		}
	}	

	// detect the element for which the term will be added
	var elementId=$("#SelectedEntityInfo").attr('lastElementID');
	if(elementId=='None'){
		return;
	}
	var start_str = $("#" + elementId).attr('start');
	var length_str = $("#" + elementId).attr('length');

	//prepare the form data
	var formData = {
		'hpoId' : hpoId,
		'hpoTerm' : hpoTerm,
		'start' : start_str
	};

	$.ajax({
		headers : {
			'Accept' : 'application/json',
			'Content-Type' : 'application/json'
		},
		type : 'POST',
		url : "Add_HPO_Term",
		data : JSON.stringify(formData),
		dataType : "json",
		success : function(terms) {
			// highlight all the terms				
			createParsedNoteHtml(terms);
			updateResultsTable(terms);
			// Update the details of the current entity
			var anno_ID=start_str + "_" + (parseInt(start_str)+parseInt(length_str));
			var curElementID='phrase_'+anno_ID;
			var curEntity=document.getElementById(curElementID);			
			showEntityDetails(curEntity,false);			
		},
		error : function(XMLHttpRequest, textStatus, errorThrown) {
			console.log("add_HPO_Term() problem!");
		}
	});
}

function RemoveAnnotationUnit(){
	var elementId=$("#SelectedEntityInfo").attr('lastElementID');
	if(elementId!='None'){
		var start_str = $("#" + elementId).attr('start');
		var length_str = $("#" + elementId).attr('length');	
		var start=parseInt(start_str);
		var length=parseInt(length_str);

		var formData = {
			'start' : start
		};
		$.blockUI({ message: '<h6> The session is being updated. Please wait! </h6>' });
	
		$.ajax({
				headers : {
					'Accept' : 'application/json',
					'Content-Type' : 'application/json'
				},
				type : 'POST',
				url : "RemoveAnnotationUnit",
				data : JSON.stringify(formData),
				dataType : "json",
				success : function(terms) {					
					createParsedNoteHtml(terms);
					updateResultsTable(terms);
					
					// select the nearest term
					var anno_ID=start + "_" + (start+length);
					var deletedElementID='phrase_'+anno_ID;
					var nearestElementID=Find_closest_entity(deletedElementID,terms);
					curEntity=document.getElementById(nearestElementID);
					showEntityDetails(curEntity);
				},
				error : function(XMLHttpRequest, textStatus, errorThrown) {
					console.log("RemoveAnnotationUnit() problem!");
				}
			});
	}
}

function validate(){
	var elementId=$("#SelectedEntityInfo").attr('lastElementID');
	if(elementId!='None'){
		var start_str = $("#" + elementId).attr('start');		
		var start=parseInt(start_str);		

		var formData = {
			'start' : start
		};
		$.blockUI({ message: '<h6> The session is being updated. Please wait! </h6>' });
	
		$.ajax({
				headers : {
					'Accept' : 'application/json',
					'Content-Type' : 'application/json'
				},
				type : 'POST',
				url : "validateAnno",
				data : JSON.stringify(formData),
				dataType : "json",
				success : function(terms) {			
					createParsedNoteHtml(terms);
					updateResultsTable(terms);
				},
				error : function(XMLHttpRequest, textStatus, errorThrown) {
					console.log("validate() problem!");
				}
			});
	}
}

function update_Neg_MCS_Asc(){
	var elementId=$("#SelectedEntityInfo").attr('lastElementID');
	if(elementId!='None'){
		var element = document.getElementById(elementId);		

		// Extract the required details from the annotated phrase:		
		//--------------------------------------------------
		// Negation status (read it from the checkbox not from the attributes of the annotated element)
		var CheckNegated = document.getElementById("CheckNegated");
		var negated=CheckNegated.checked
		//--------------------------------------------------
		// Mutiple cinical signs
		var CheckMCS = document.getElementById("CheckMCS");
		var mult_CS=CheckMCS.checked		
		//--------------------------------------------------
		// concerned_person
		var concerned_person=document.getElementById("selectPatientAascendant").value;
		
		//--------------------------------------------------
		// start and length
		var start_str = $("#" + elementId).attr('start');
		var length_str = $("#" + elementId).attr('length');
		var start=parseInt(start_str);		
		
		//--------------------------------------------------
		// Update the terms in the user session
		var formData = {
			'negated' : negated,
			'mult_CS' : mult_CS,
			'concerned_person' :concerned_person,
			'start' : start
		};
		$.blockUI({ message: '<h6> The session is being updated. Please wait! </h6>' });
	
		$.ajax({
				headers : {
					'Accept' : 'application/json',
					'Content-Type' : 'application/json'
				},
				type : 'POST',
				url : "update_Neg_MCS_Asc",
				data : JSON.stringify(formData),
				dataType : "json",
				success : function(terms) {			
					createParsedNoteHtml(terms);
					updateResultsTable(terms);
				},
				error : function(XMLHttpRequest, textStatus, errorThrown) {
					console.log("update_Neg_MCS_Asc() problem!");
				}
			});
	}
}

function AddTerm_Mouse_Enter(start,length){
	start=parseInt(start);
	length=parseInt(length);
	var formData = {
		'start' : start,
		'length' : length		
	};
	$.blockUI({ message: '<h6> The session is being updated. Please wait! </h6>' });

	$.ajax({
			headers : {
				'Accept' : 'application/json',
				'Content-Type' : 'application/json'
			},
			type : 'POST',
			url : "AddTerm_Mouse_Enter",
			data : JSON.stringify(formData),
			dataType : "json",
			success : function(terms) {
				// highlight all the terms				
				createParsedNoteHtml(terms);
				updateResultsTable(terms);
				// select the last added term
				var anno_ID=start + "_" + (start+length);
				var curElementID='phrase_'+anno_ID;
				var curEntity=document.getElementById(curElementID);	
				if(curEntity==null) // it might be null only when adding a term manually on the top of existing terms
				{
					closestElementID=Find_closest_entity(curElementID,terms);
					curEntity=document.getElementById(closestElementID);
				}
				showEntityDetails(curEntity);
			},
			error : function(XMLHttpRequest, textStatus, errorThrown) {
				console.log("AddTerm_Mouse_Enter() problem!");
			}
		});
}

function Find_closest_entity(ElementID,terms){
	if(terms.length==0){
		return "None";
	}

	var id_segments = ElementID.split("_"); // phrase_start_length
	var start = id_segments[1];
	var length = id_segments[2];
	var end= start+length-1;

	var distance=1000000;
	bestIndex=0;

	for (let i = 0; i <terms.length; i++) {
		var startIndex=terms[i]['start'];
		var endIndex=startIndex+terms[i]['length'];
		var curDistance=Math.abs(startIndex-start);
		curDistance=Math.min(curDistance,Math.abs(endIndex-start));
		if(curDistance<distance){
			bestIndex=i;
			distance=curDistance;
		}	
	}

	var startIndex=terms[bestIndex]['start'];
	var endIndex=startIndex+terms[bestIndex]['length'];
	var anno_ID=startIndex + "_" + endIndex;
	var closestElementID='phrase_'+anno_ID;
	
	return closestElementID;
}

function createParsedNoteHtml(terms) {
	var note = $("#noteTextarea").val();
	var parsedNoteHtml = note;
	var selElementId=$("#SelectedEntityInfo").attr('lastElementID');
	for (let i = terms.length-1; i >=0; i--) {
		var startIndex=terms[i]['start'];
		var endIndex=startIndex+terms[i]['length'];

		var anno_ID=startIndex + "_" + endIndex;
		var AnnotatedPhrase=note.substring(startIndex, endIndex);

		var curElementID='phrase_'+anno_ID;

		var spanClass="highlight-proposed";
		if(terms[i]['validated']){
			spanClass="highlight-validated";
		}

		if(selElementId==curElementID){
			spanClass+=" highlight-selected";
			console.log(spanClass);
		}
		

		var strStart='<span onclick="showEntityDetails(this)"'+
		    'class= "'+spanClass+'"'+
			' start="'+ terms[i]['start'] +'"'+
			' length="'+ terms[i]['length'] +'"'+
			' phrase="'+ AnnotatedPhrase +'"'+
			' negated="' + terms[i]['negated'] +'"'+
			' concerned_person="'+terms[i]['concerned_person']+'"'+
			' mult_CS="' + terms[i]['mult_CS'] +'"'+
			' hpoAnnotation=\'' + JSON.stringify(terms[i]['hpoAnnotation']).replace("'","&apos") +'\''+
			' id= ' + curElementID + '>';
		var strEnd='</span>';		

		parsedNoteHtml=parsedNoteHtml.substring(0, endIndex) + strEnd + parsedNoteHtml.substring(endIndex, parsedNoteHtml.length);
		parsedNoteHtml=parsedNoteHtml.substring(0, startIndex) + strStart + parsedNoteHtml.substring(startIndex, parsedNoteHtml.length);
	}
	document.getElementById("id_ParsedNote").innerHTML = parsedNoteHtml;
}

function showEntityDetails(entity,ResetSearchTable=true) {
	if(ResetSearchTable){
		Init_Search_Results_Table();
	}	
	if(entity==null) // it might be null only when adding a term manually on the top of existing terms
	{
		Reset_Annotated_Phrase_Panel();
		return;
	}
	// Thickly outline the selected entity	
	entity.classList.add("highlight-selected");

	// remove the thick outline from the previously selected element (if exists)
	var elementId=$("#SelectedEntityInfo").attr('lastElementID');
	if((elementId!='None')&&(elementId!=entity.id)){			
		var element = document.getElementById(elementId);
		if(element!=null) // it might be null only when adding a term manually on the top of existing terms
		{
			element.classList.remove("highlight-selected");
		}
		
	}

	// store the ID of the selected entity in the item SelectedEntityInfo (to remember the previously selected one)
	$("#SelectedEntityInfo").attr('lastElementID',entity.id);

	// get and show the selected phrase in the details panel
	var phrase = $("#" + entity.id).attr('phrase');
	document.getElementById("SelectedEntityInfo").innerHTML = phrase;

	// get and show the negation status
	var negated=true;
	var negStr = $("#" + entity.id).attr('negated');
	if(negStr=="false")
	{
		negated=false;
	}
	$("#CheckNegated").prop('checked', negated);

	// get and show the mult_CS
	var mult_CS=true;
	var MCS_str = $("#" + entity.id).attr('mult_CS');
	if(MCS_str=="false")
	{
		mult_CS=false;
	}
	$("#CheckMCS").prop('checked', mult_CS);

	// get and show the concerned_person	
	var concerned_person = $("#" + entity.id).attr('Concerned_Person');
	document.getElementById("selectPatientAascendant").value = concerned_person;

	// get start and length (to be used later for modifying the annotation range)
	var start_str = $("#" + entity.id).attr('start');
	var length_str = $("#" + entity.id).attr('length');
	var start=parseInt(start_str);
	var length=parseInt(length_str);
	//document.getElementById("SelectedEntityInfo").innerHTML = phrase+ " ("+start_str+"_"+length_str+")"; // Remove this line ! it is used now only for development purposes

	// update the terms table
	show_HPO_Term_Details_Table(entity);
}

function show_HPO_Term_Details_Table(entity){
	var start=0;
	var length=0;
	var hpoAnnotation=[];
	if(entity){
		start = $("#" + entity.id).attr('start');
		length = $("#" + entity.id).attr('length');
		
		var RawAnno = $("#" + entity.id).attr('hpoAnnotation');
		RawAnno=RawAnno.replace("&apos","'");
		hpoAnnotation=JSON.parse(RawAnno);
	}	
	
	var json_terms = [];
	for (let i = 0; i< hpoAnnotation.length; i++) {
		hpoId=hpoAnnotation[i]['hpoId'];
		parserID=hpoAnnotation[i]['parser'];
		//hpoId_href = '<a href="javascript:show_HPO_term_details(\''+hpoId+'\');">'+hpoId+'</a>';
		hpoName=hpoAnnotation[i]['hpoName'];
		ratingVal=parseInt(hpoAnnotation[i]['rating']);

		var starWhite= "far fa-star star-rating";
		var starBlack= "fas fa-star star-rating";

		var star1_class=starWhite;
		var star2_class=starWhite;
		var star3_class=starWhite;

		//alert(ratingVal)

		switch(ratingVal){
			case 3:
				star1_class=starBlack;
				star2_class=starBlack;
				star3_class=starBlack;
				break;
			case 2:
				star1_class=starBlack;
				star2_class=starBlack;
				break;
			case 1:
				star1_class=starBlack;
				break;
		}
		if(ratingVal==3){
			star1_class=starBlack;
			star2_class=starBlack;
			star3_class=starBlack;
		}

		var IDstr=hpoId + "_"+start+"_"+length;
		var star1_ID="star_1_" + IDstr;
		var star2_ID="star_2_" + IDstr;
		var star3_ID="star_3_" + IDstr;
		rating=	'<i class="' + star1_class + '" id= "' + star1_ID + '" onclick="starClicked(this)"></i>'+
				'<i class="' + star2_class + '" id= "' + star2_ID + '" onclick="starClicked(this)"></i>'+
				'<i class="' + star3_class + '" id= "' + star3_ID + '" onclick="starClicked(this)"></i>';

		ratingInit=hpoAnnotation[i]['ratingInit'];

		// prepare the Action buuton "remove"
		// we assume that the HPO IDs in this table are unique (because we remove duplicates in the backend)
		var spanClass="button-remove-term";		
				
		var ActionStr='<span onclick="remove_HPO_Term(this)"'+
			'class= "'+spanClass+'"'+
			' id= rm_' + hpoId + '_'+start+'_'+length+			
			'><i class="fa fa-trash"></i></span>';
		
		strStart='<span onclick="info_HPO_Term(this)"'+
		'class= "'+spanClass+'"'+	
		' id= ' + hpoId+ '_'+parserID +'>';
		strEnd='<i class="fas fa-info"></i></span>';
		ActionStr=	ActionStr+strStart+strEnd;

		dictTemp={
			"ID": hpoId,
			"Term": hpoName,
			"Rating": rating,
			"InitRating": ratingInit,
			"Actions" : ActionStr
		};
		json_terms.push(dictTemp);
	}

	var table = $('#termDetailesTable').DataTable(
	{
		"data" : json_terms,
		"columns" : [
				{
					"data" : "ID"
				},
				{
					"data" : "Term"
				},
				{
					"data" : "Rating"
				},
				{
					"data" : "InitRating"
				},
				{
					"data" : "Actions"
				}
		],
		autoWidth: false,
		responsive : true,
		lengthChange : true,
		buttons : [ 'excel', 'pdf' ],
		searching : false,
		paging : false,
		info : false,
		"bDestroy" : true
	});
	table.column( '3:visible' ).order( 'desc' ).draw();	
}

function starClicked(star){
	ctrlID=star.id;
	var id_segments = ctrlID.split("_"); // star_starNumber_hpoId_start_length
	var starNum = id_segments[1];	
	var hpoId = id_segments[2];
	var start = id_segments[3];
	var length = id_segments[4];
	updateRating(start,length,hpoId,starNum);	 
}

function updateRating(start,length,hpoId,starNum){
	//alert("Star : "+starNum+ " HPO_ID : "+hpoId+ " start : "+start+ " length : "+length)
	var formData = {
		'start' : start,		
		'hpoId' : hpoId,
		'starNum' : starNum
	};

	$.ajax({
		headers : {
			'Accept' : 'application/json',
			'Content-Type' : 'application/json'
		},
		type : 'POST',
		url : "updateTermRating",
		data : JSON.stringify(formData),
		dataType : "json",
		success : function(terms) {
			// highlight all the terms				
			createParsedNoteHtml(terms);
			updateResultsTable(terms);
			// Update the details of the current entity
			var anno_ID=start + "_" + (parseInt(start)+parseInt(length));
			var curElementID='phrase_'+anno_ID;
			var curEntity=document.getElementById(curElementID);			
			showEntityDetails(curEntity,false);
		},
		error : function(XMLHttpRequest, textStatus, errorThrown) {
			console.log("updateRating() problem!");
		}
	});
}

function remove_HPO_Term(term){	
	ctrlID=term.id;
	var id_segments = ctrlID.split("_"); // rm_HpoID_start_length
	var hpoId = id_segments[1];
	var start = id_segments[2];
	var length = id_segments[3];

	var formData = {
		'start' : start,		
		'hpoId' : hpoId
	};

	$.ajax({
		headers : {
			'Accept' : 'application/json',
			'Content-Type' : 'application/json'
		},
		type : 'POST',
		url : "Remove_HPO_Term",
		data : JSON.stringify(formData),
		dataType : "json",
		success : function(terms) {
			// highlight all the terms				
			createParsedNoteHtml(terms);
			updateResultsTable(terms);
			// Update the details of the current entity
			var anno_ID=start + "_" + (parseInt(start)+parseInt(length));
			var curElementID='phrase_'+anno_ID;
			var curEntity=document.getElementById(curElementID);			
			showEntityDetails(curEntity,false);
		},
		error : function(XMLHttpRequest, textStatus, errorThrown) {
			console.log("remove_HPO_Term() problem!");
		}
	});
}

function updateResultsTable(terms){
	var note = $("#noteTextarea").val();	
	
	var json_terms = [];
	for (let i =0; i < terms.length; i++) {
		var startIndex=terms[i]['start'];
		var endIndex=startIndex+terms[i]['length'];
		var AnnotatedPhrase=note.substring(startIndex, endIndex);
		var negated=terms[i]['negated'];
		var concerned_person=terms[i]['concerned_person'];
		var hpoAnnotation=terms[i]['hpoAnnotation'];

		for (let j = 0; j< hpoAnnotation.length; j++) {
			hpoId=hpoAnnotation[j]['hpoId'];
			hpoId = '<a href="javascript:show_HPO_term_details(\''+hpoId+'\');">'+hpoId+'</a>';
			hpoName=hpoAnnotation[j]['hpoName'];
			rating=hpoAnnotation[j]['rating'];			
			dictTemp={
				"Phrase" : AnnotatedPhrase,
				"ID": hpoId,
				"Term": hpoName,
				"Is_negated" : negated,
				"Patient" : concerned_person,
				"Score": rating			
			};
			json_terms.push(dictTemp);
		}			
	}	

	var table = $('#resultsTable').DataTable(
	{
		"data" : json_terms,
		"columns" : [
				{"data" : "Phrase", "width": "33.33%"},
				{"data" : "ID", "width": "8.33%"},
				{"data" : "Term", "width": "33.33%"},
				{"data" : "Is_negated", "width": "8.33%"},
				{"data" : "Patient", "width": "8.33%"},
				{"data" : "Score", "width": "8.33%"}
		],
		responsive : true,
		lengthChange : true,
		buttons : [ 'excel', 'pdf' ],
		searching : false,
		paging : false,
		info : false,
		"bDestroy" : true
	});
	table.column( '5:visible' ).order( 'desc' ).draw();	
}

function isSelectionOnlyIn(yourDiv) {
	var sel = window.getSelection();
	if (sel.rangeCount < 1) return false;
	var range = sel.getRangeAt(0);
	if (range.collapsed) return false;
	var cont = range.commonAncestorContainer;
  
	return ($(cont) === $(yourDiv) || $(cont).parents(yourDiv).length > 0);
}

function insertTermEnterkey(){

	if(isSelectionOnlyIn("#id_Parsed_Div")){
		if (typeof window.getSelection != "undefined") {
			text = String(window.getSelection());
			if (text.length < 5) {
				resetTermEnterkey_attr();
				return;
			}
			var start = 0;
			var end = 0;
			var context = document.querySelector("#id_ParsedNote");				
			var range = window.getSelection().getRangeAt(0);					
			var priorRange = range.cloneRange();
			priorRange.selectNodeContents(context);
			priorRange.setEnd(range.startContainer,range.startOffset);
			start = priorRange.toString().length;
			end = start + text.length - 1;
			length = end - start + 1;
	
			document.getElementById("insertTermMouseEnter").selectedText = text;
			document.getElementById("insertTermMouseEnter").start = start;
			document.getElementById("insertTermMouseEnter").length = length;

			//Add new term to the session
			AddTerm_Mouse_Enter(start,length);
		}
	}else{
		resetTermEnterkey_attr();
	}
}

function resetTermEnterkey_attr(){
	document.getElementById("insertTermMouseEnter").selectedText = "";
	document.getElementById("insertTermMouseEnter").start = 0;
	document.getElementById("insertTermMouseEnter").length = 0;
}

function ParserID2Name(id){
	if(id=="Manual")
		return "Manual annotation";
	if(id=="StrMatch")
		return "String matching-based parser";
	if(id=="ENLIGHTOR")
		return "b<>com ENLIGHTOR";
	return "Unknown parser!"
}

function show_HPO_term_details(HPO_ID,ParserID="None") {

	var termDetails=getHpoTermDetails(HPO_ID);

	var res_hpoID = termDetails["ID"];
	var res_HpoName=termDetails["name"];
	var res_Def=termDetails["Def"];
	var res_Synonyms=""
	for (i=0; i<termDetails["Synonyms"].length;i++){
		res_Synonyms+="- "+termDetails["Synonyms"][i]+"<br>";
	}

	
	var res_Hierarchy=""
	for (i=1; i<termDetails["Hierarchy"].length-1;i++){
		res_Hierarchy+="- "+termDetails["Hierarchy"][i]+"<br>";
	}

	var myWindow = window.open("", "MsgWindow", "screenX=-200, screenY=500, width=400,height=500");
	
	var content =   '<html>'+
					'<head>'+
						'<title>HPO Term info</title>'+
						'<style>'+		
						'table {'+		
						'font-family: arial, sans-serif;'+
						'border-collapse: collapse;'+		
						'width: 100%;'+		
						'}'+		
						'td, th {'+		
						'border: 1px solid #dddddd;'+		
						'text-align: left;'+		
						'padding: 8px;'+		
						'}'+		
						'tr:nth-child(even) {'+		
						'background-color: #dddddd;'+		
						'}'+		
						'</style>'+				
					'</head>'+
					'<body>	'
	if(ParserID!="None"){
		content=content+'<h3>Parsing sources:</h3>'+
						'<ul>'
		var parserIds = ParserID.split(";"); // HpoID_ParserID
		for(i in parserIds){			
			content=content+'<li>'+ParserID2Name(parserIds[i])+'</li>'
		}
		content=content+'</ul>'
	}
	content=content+'<h3>HPO term description:</h3>'
	content=content+'<table id="termOboInfoTable">'+
						'<tr>'+
							'<td><b>ID</b></td>'+
							'<td>'+res_hpoID+'</td>'+
						'</tr>'+
						'<tr>'+
							'<td><b>Term</b></td>'+
							'<td>'+res_HpoName+'</td>'+
						'</tr>'+
						'<tr>'+
							'<td><b>Definition</b></td>'+
							'<td>'+res_Def+'</td>'+
						'</tr>'+
						'<tr>'+
							'<td><b>Synonyms</b></td>'+
							'<td>'+res_Synonyms+'</td>'+
						'</tr>'+
						'<tr>'+
							'<td><b>Hierarchy</b></td>'+
							'<td>'+res_Hierarchy+'</td>'+
						'</tr>'+
					'</table>';	
	content=content+'</body>'+'</html>';

	myWindow.document.body.innerHTML = '';
	myWindow.document.write(content);
}

function getHpoTermDetails(HPO_ID){
	var formData = {
		'hpoId' : HPO_ID
	};
	reqRes=$.ajax({
		headers : {
			'Accept' : 'application/json',
			'Content-Type' : 'application/json'
		},
		type : 'POST',
		async: !1,
		url : "getHpoTermDetails",
		data : JSON.stringify(formData),
		dataType : "json",
		success : function(data) {
		},
		error : function(XMLHttpRequest, textStatus, errorThrown) {
			alert('Error occured');
			return;
		}
	});
	return reqRes.responseJSON['termDetails'];
}


function get_annotation_results(){

	annotation_results = $.ajax({
		headers : {
			'Accept' : 'application/json',
			'Content-Type' : 'application/json'
		},
		type : 'GET',
		url : "get_annotation_results",
		dataType : "json",
		async: false,
		success : function(data) {			
		},
		error : function(XMLHttpRequest, textStatus, errorThrown) {
			console.log("get_annotation_results() problem!");
		}
	}).responseJSON;
	return annotation_results;
}

function get_annotator_ID(){
	annotator_ID = $.ajax({
		headers : {
			'Accept' : 'application/json',
			'Content-Type' : 'application/json'
		},
		type : 'GET',
		url : "get_annotator_ID",
		dataType : "json",
		async: false,
		success : function(data) {			
		},
		error : function(XMLHttpRequest, textStatus, errorThrown) {
			console.log("get_annotator_id() problem!");
		}
	}).responseJSON;
	return annotator_ID;
}

function get_source_ID(){
	source_ID = $.ajax({
		headers : {
			'Accept' : 'application/json',
			'Content-Type' : 'application/json'
		},
		type : 'GET',
		url : "get_source_ID",
		dataType : "json",
		async: false,
		success : function(data) {			
		},
		error : function(XMLHttpRequest, textStatus, errorThrown) {
			console.log("get_source_id() problem!");
		}
	}).responseJSON;
	return source_ID;
}