let starting_date = null;
let starting_date_input = null;
let ending_date = null;
let ending_date_input = null;

function setupApp() {
    console.log('MainJs is ready');
}

function handleFormInput(element) {
    label_element = element.parentElement.getElementsByTagName('label')[0]
    console.log(label_element);
    label_element.setAttribute('class', 'smallLabel');
    if (element.value == "") {
        label_element.removeAttribute('class', 'smallLabel');
    }
}
function  handleFormInput_startdate(element) {
    label_element = element.parentElement.getElementsByTagName('label')[0]
    console.log(label_element);
    label_element.setAttribute('class', 'smallLabel');
    if (element.value == "") {
        label_element.removeAttribute('class', 'smallLabel');
    }
    starting_date = element.value;
    starting_date_input = element;
}
function  handleFormInput_enddate(element) {
    label_element = element.parentElement.getElementsByTagName('label')[0]
    console.log(label_element);
    label_element.setAttribute('class', 'smallLabel');
    if (element.value == "") {
        label_element.removeAttribute('class', 'smallLabel');
    }
    ending_date = element.value;
    ending_date_input = element;
    if (ending_date > starting_date) {
        console.log('Good Information')
    } else {
        console.log('Bad Information')
        starting_date = ending_date;
        starting_date_input.value = element.value;
    }
}

