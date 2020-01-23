/* globals failAlert */
/* globals templateController */
/* globals graphController */
/* globals fetchJson */


/* exported graphFormController */
const graphFormController = (() => {
	'use strict';

	const DOM = {};

	const graphPanel = graphController;

	/* PUBLIC METHODS */
	function init() {
		graphPanel.init();
		cacheDom();
		bindUIEvents();
		updateForm();
	}

	/* PRIVATE METHODS */
	function bindUIEvents() {

		document.getElementById('saveButton').addEventListener('click', () => {
			if (graphPanel.graphIsValid())
				saveGraph();
			else {
				failAlert('La séquence n\'est pas valide, certains noeuds n\'ont pas de parent.');
			}
		});

		document.querySelector('select[name=newNodeTypeChoice]').addEventListener('change', () => {
			updateForm();
		});

		document.querySelectorAll('a[name=editSeq]').forEach((e) => {
			e.addEventListener('click', () => {
				const seq_name = e.id.substring(e.id.indexOf('_') + 1);
				console.log(seq_name);

				editSequence(seq_name);
				templateController.getAccordion('creation').open();
				window.location.hash = '#creation';
			});
		});
	}

	function cacheDom() {
		DOM.$motionOptions = document.getElementById('motionOptions');
		DOM.$servoOptions = document.getElementById('servoOptions');
		DOM.$relayOptions = document.getElementById('relayOptions');
		DOM.$speechOptions = document.getElementById('speechOptions');
		DOM.$scriptOptions = document.getElementById('scriptOptions');
		DOM.$soundOptions = document.getElementById('soundOptions');
		DOM.$pauseOptions = document.getElementById('pauseOptions');
		DOM.$servoSequenceOptions = document.getElementById('servoSequenceOptions');
		DOM.$name = document.getElementById('name');
	}

	/**
	 * Update the form to display the options corresponding to the type of button chosen
	 */
	function updateForm() {
		DOM.$motionOptions.classList.add('hide');
		DOM.$servoOptions.classList.add('hide');
		DOM.$relayOptions.classList.add('hide');
		DOM.$speechOptions.classList.add('hide');
		DOM.$scriptOptions.classList.add('hide');
		DOM.$soundOptions.classList.add('hide');
		DOM.$pauseOptions.classList.add('hide');
		DOM.$servoSequenceOptions.classList.add('hide'); // COMPATIBILITY REASON
		if (document.querySelector('select[name=newNodeTypeChoice]').value !== '') {
			const selectedNodeType = document.querySelector('select[name=newNodeTypeChoice]');
			document.getElementById(selectedNodeType.value + 'Options').classList.remove('hide');
		} else {
			console.warn('Aucune action n\'a été selectionnée !');
		}
	}

	/**
	 * Save the graph on the server
	 */
	function saveGraph() {
		const sequence = graphPanel.getGraph();
		console.log(sequence);

		fetchJson('/save_sequence', 'POST', {seq_name:DOM.$name.value, seq_data:sequence})
			.then(()=> {
				location.reload();
			});
	}

	/**
	 * Edit the specified sequence
	 * @param {string} seqName the name of the sequence to edit
	 */
	function editSequence(seqName) {
		DOM.$name.value = seqName;
		const sequenceData = document.getElementById('data_' + seqName).innerHTML;
		const json = JSON.parse(sequenceData);
		graphPanel.updateGraph(json);
	}

	return {
		init: init
	};
})();