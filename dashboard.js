const updateGraph = (graph, label, time, data) => {
    if(graph.config.data.labels.length >= 30) {
        graph.config.data.labels.shift();
        graph.config.data.datasets[0].data.shift();
        graph.config.data.datasets[1].data.shift();
        graph.config.data.datasets[2].data.shift();
    }

    graph.config.data.labels.push(time + ':00');
    graph.config.data.datasets[0].data.push(data.energy_usage);
    graph.config.data.datasets[1].data.push(data.energy_production);
    graph.config.data.datasets[2].data.push(data.energy_netto);
    graph.update();

    label_string = '#' + label + '_average_label';
    document.querySelector(label_string).innerHTML = 'Netto Durchschnitt: ' + data.energy_netto_average;

    if (label === 'general') return;

    label_string = '#' + label + '_wetter_label';
    document.querySelector(label_string).innerHTML = 'Wetter: ' + data.weather;
}

const updateSpeicher = (graph, time, data) => {
    if(graph.config.data.labels.length >= 30) {
        graph.config.data.labels.shift();
        graph.config.data.datasets[0].data.shift();
    }

    graph.config.data.labels.push(time + ':00');
    graph.config.data.datasets[0].data.push(data.stromspeicher_prozent);
    graph.update();

    label_string = '#stromspeicher_label';
    document.querySelector(label_string).innerHTML = 'Speicher in kW: ' + data.stromspeicher;
}

let loop = async () => {
     const url = new URL('http://172.16.221.2:6969/getData');
    //const url = new URL('http://127.0.0.1:6969/getData')
    let res = await fetch(url);
    res = await res.json();
    if(res === null) return;
    res = res.data;
    console.log(res);


    updateSpeicher(stromspeicher_chart, res.time, res.general);
    updateGraph(general_energy_chart, 'general', res.time, res.general);
    updateGraph(central_energy_chart, 'central', res.time, res.central);
    updateGraph(wohnblock_energy_chart, 'wohnblock', res.time, res.wohnblock);
    updateGraph(krankenhaus_energy_chart, 'krankenhaus', res.time, res.krankenhaus);
}



const stromspeicher_chart = new Chart(
    document.querySelector('#stromspeicher_chart'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Stand in %',
                    backgroundColor: 'red',
                    borderColor: 'red',
                    data: [],
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                yAxes: {
                    beginAtZero: true
                }
            },
            animation: {
                easing: 'linear'
            }
        }
    }
);

const general_energy_chart = new Chart(
    document.querySelector('#general_energy_chart'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Energie Verbrauch',
                    backgroundColor: 'red',
                    borderColor: 'red',
                    data: [],
                },
                {
                    label: 'Energie Produktion',
                    backgroundColor: 'green',
                    borderColor: 'green',
                    data: [],
                },
                {
                    label: 'Energie Netto',
                    backgroundColor: 'blue',
                    borderColor: 'blue',
                    data: [],
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                yAxes: {
                    beginAtZero: true
                }
            },
            animation: {
                easing: 'linear'
            }
        }
    }
);

const central_energy_chart = new Chart(
    document.querySelector('#central_energy_chart'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Energie Verbrauch',
                    backgroundColor: 'red',
                    borderColor: 'red',
                    data: [],
                },
                {
                    label: 'Energie Produktion',
                    backgroundColor: 'green',
                    borderColor: 'green',
                    data: [],
                },
                {
                    label: 'Energie Netto',
                    backgroundColor: 'blue',
                    borderColor: 'blue',
                    data: [],
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                yAxes: {
                    beginAtZero: true
                }
            },
            animation: {
                easing: 'linear'
            }
        }
    }
);

const wohnblock_energy_chart = new Chart(
    document.querySelector('#wohnblock_energy_chart'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Energie Verbrauch',
                    backgroundColor: 'red',
                    borderColor: 'red',
                    data: [],
                },
                {
                    label: 'Energie Produktion',
                    backgroundColor: 'green',
                    borderColor: 'green',
                    data: [],
                },
                {
                    label: 'Energie Netto',
                    backgroundColor: 'blue',
                    borderColor: 'blue',
                    data: [],
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                yAxes: {
                    beginAtZero: true
                }
            },
            animation: {
                easing: 'linear'
            }
        }
    }
);

const krankenhaus_energy_chart = new Chart(
    document.querySelector('#krankenhaus_energy_chart'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Energie Verbrauch',
                    backgroundColor: 'red',
                    borderColor: 'red',
                    data: [],
                },
                {
                    label: 'Energie Produktion',
                    backgroundColor: 'green',
                    borderColor: 'green',
                    data: [],
                },
                {
                    label: 'Energie Netto',
                    backgroundColor: 'blue',
                    borderColor: 'blue',
                    data: [],
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                yAxes: {
                    beginAtZero: true
                }
            },
            animation: {
                easing: 'linear'
            }
        }
    }
);

setInterval(loop, 100ü);
