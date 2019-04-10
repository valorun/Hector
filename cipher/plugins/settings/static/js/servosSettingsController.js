var servosSettingsController = {
	init: function () {
		this.bind();
	},
	bind: function () {
		$('#addServo').on('click', function () {
			let label = $('#newServoLabel').val();
			let pin = $('#newServoPin').val();
			let min_pulse_width = parseInt($('#newServoMinPulseWidth').val());
			let max_pulse_width = parseInt($('#newServoMaxPulseWidth').val());
			let def_pulse_width = parseInt($('#newServoDefPulseWidth').val());
			let raspi_id = $('#newServoRaspiId').val();
			console.log(min_pulse_width);

			$.ajax({
				type: 'POST',
				url: '/save_servo',
				data: { servo_label: label, servo_pin: pin, min_pulse_width: min_pulse_width, max_pulse_width: max_pulse_width, def_pulse_width: def_pulse_width, raspi_id: raspi_id },
				success: function () {
					location.reload();
				},
				error: function (request) {
					failAlert(request.responseText);
				}
			});
		});
		//checkbox to enable or disable the servo
		$('input[name=enableServo]').on('change', (e) => {
			let servo_label = e.currentTarget.id.substr(e.currentTarget.id.indexOf('_') + 1);
			this.enableServo(servo_label, $(e.currentTarget).prop('checked'));
		});

		//button to delete the servo
		$('a[name=deleteServo]').on('click', (e) => {
			let servo_label = e.currentTarget.id.substr(e.currentTarget.id.indexOf('_') + 1);
			this.deleteServo(servo_label);
		});
	},

	/**
 	 *  Enable OR disable a servo
	  *	@param	{string} servo_label servo label
	  *	@param	{boolean} value new state for the servo
 	 */
	enableServo: function (servo_label, value) {
		$.ajax({
			type: 'POST',
			url: '/enable_servo',
			data: { servo_label: servo_label, value: value },
			success: function () {
				console.log(servo_label + ' updated');
			},
			error: function (request) {
				failAlert(request.responseText);
			}
		});
	},

	/**
 	 *  Delete a servo
 	 *	@param	{string} servo_label relay label
 	 */
	deleteServo: function (servo_label) {
		var confirm = window.confirm('Etes vous sûr de vouloir supprimer le servomoteur \'' + servo_label + '\' ?');
		if (confirm) {
			$.ajax({
				type: 'POST',
				url: '/delete_servo',
				data: { servo_label: servo_label },
				success: () => {
					console.log(servo_label + ' deleted');
					$('#' + servo_label).remove();
				},
				error: (request) => {
					failAlert(request.responseText);
				}
			});
		}
	}
};
