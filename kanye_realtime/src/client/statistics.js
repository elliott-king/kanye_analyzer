import Chart from 'chart.js';
import pattern from 'patternomaly';

import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

var xhr = new XMLHttpRequest();
xhr.onreadystatechange = displayContent;
xhr.open('GET', 'data.json');
xhr.send();

function displayContent() {
    if (xhr.readyState ==  XMLHttpRequest.DONE) {
        if (xhr.status == 200) {
            var data = JSON.parse(xhr.responseText);
            console.log(data);

            // Examples using Chart.js, taken from:
            // https://mdbootstrap.com/docs/jquery/javascript/charts/
            var ctxPositivity = document.getElementById("positivity-chart").getContext('2d');
            var positivityChart = new Chart(ctxPositivity, {
                type: 'pie',
                data: {
                    labels: Object.keys(data.positivity_statistics),
                    datasets: [{
                        data: Object.values(data.positivity_statistics),
                        backgroundColor: ["#F7464A", "#46BFBD", "#FDB45C", "#949FB1", "#4D5360"],
                        hoverBackgroundColor: ["#FF5A5E", "#5AD3D1", "#FFC870", "#A8B3C5", "#616774"]
                    }]
                },
                options: {
                    responsive: true
                }
            });

            console.log('colors:',[...Array(11).keys()].map(x => rainbow(11, x)));
            var ctxCategory = document.getElementById("category-chart").getContext('2d');
            var categoryChart = new Chart(ctxCategory, {
                type: 'pie',
                data: {
                    labels: Object.keys(data.category_statistics),
                    datasets: [{
                        data: Object.values(data.category_statistics),
                        backgroundColor: pattern.generate([...Array(10).keys()].map(x => rainbow(10, x))),
                        // backgroundColor: ["#F7464A", "#46BFBD", "#FDB45C", "#949FB1", "#4D5360"],
                        // backgroundColor: []
                        // hoverBackgroundColor: ["#FF5A5E", "#5AD3D1", "#FFC870", "#A8B3C5", "#616774"]
                    }]
                },
                options: {
                    responsive: true
                }
            });
        } else {
            console.error("Problem with retrieving data");
        }
    }
}

// https://stackoverflow.com/questions/1484506/random-color-generator
function rainbow(numOfSteps, step) {
    // This function generates vibrant, "evenly spaced" colours (i.e. no clustering). This is ideal for creating easily distinguishable vibrant markers in Google Maps and other apps.
    // Adam Cole, 2011-Sept-14
    // HSV to RBG adapted from: http://mjijackson.com/2008/02/rgb-to-hsl-and-rgb-to-hsv-color-model-conversion-algorithms-in-javascript
    var r, g, b;
    var h = step / numOfSteps;
    var i = ~~(h * 6);
    var f = h * 6 - i;
    var q = 1 - f;
    switch(i % 6){
        case 0: r = 1; g = f; b = 0; break;
        case 1: r = q; g = 1; b = 0; break;
        case 2: r = 0; g = 1; b = f; break;
        case 3: r = 0; g = q; b = 1; break;
        case 4: r = f; g = 0; b = 1; break;
        case 5: r = 1; g = 0; b = q; break;
    }
    var c = "#" + ("00" + (~ ~(r * 255)).toString(16)).slice(-2) + ("00" + (~ ~(g * 255)).toString(16)).slice(-2) + ("00" + (~ ~(b * 255)).toString(16)).slice(-2);
    return (c);
}
