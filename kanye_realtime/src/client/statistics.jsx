var xhr = new XMLHttpRequest();
xhr.onreadystatechange = displayContent;
xhr.open('GET', 'data.json');
xhr.send();

function displayContent() {
    if (xhr.readyState ==  XMLHttpRequest.DONE) {
        if (xhr.status == 200) {
            console.log('Result of GET json:', xhr.responseText);
        } else {
            console.error("Problem with retrieving data");
        }
    }
}