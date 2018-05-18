def organise_entries(entries):
	json_entries = []
	names = []

	for counter,item in enumerate(entries):
		json_object_name = item['#0']['archetype_details']['template_id']['value']
		json_object_value = str(counter)

		for i in range(len(names)):
			if json_object_name[i] == names[i]:
				json_entries[i]['value'].append(json_object_value)
		else:
			json_object['name'] = json_object_name
			json_object['value'] = [json_object_value]
			json_entries.append(json_object)
			json_object = {}

	return json_entries

data = [
      {
        "name": "Medications",
        "value": "0"
      },
      {
        "name": "Medical Diagnosis",
        "value": "1"
      },
      {
        "name": "Medical Diagnosis",
        "value": "2"
      },
      {
        "name": "Medical Diagnosis",
        "value": "3"
      },
      {
        "name": "Medical Diagnosis",
        "value": "4"
      },
      {
        "name": "Allergies",
        "value": "5"
      },
      {
        "name": "Laboratory Report",
        "value": "6"
      },
      {
        "name": "Laboratory Report",
        "value": "7"
      },
      {
        "name": "Laboratory Report",
        "value": "8"
      },
      {
        "name": "Laboratory Report",
        "value": "9"
      },
      {
        "name": "Vital Signs",
        "value": "10"
      },
      {
        "name": "Vital Signs",
        "value": "11"
      },
      {
        "name": "Vital Signs",
        "value": "12"
      },
      {
        "name": "Vital Signs",
        "value": "13"
      },
      {
        "name": "Vital Signs",
        "value": "14"
      },
      {
        "name": "Vital Signs",
        "value": "15"
      },
      {
        "name": "Parental Growth",
        "value": "16"
      },
      {
        "name": "Measurement ECG Report",
        "value": "17"
      },
      {
        "name": "Measurement ECG Report",
        "value": "18"
      }
    ]
		
print(organise_entries(data))