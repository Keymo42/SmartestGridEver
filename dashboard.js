const formatNumber = (number) => {
    number = number * 100;
    number = Math.round(number);
    number = number / 100;
    return number;
}

const updateGraph = (graph, label, time, data) => {
    if(graph.config.data.labels.length >= 30) {
        graph.config.data.labels.shift();
        graph.config.data.datasets[0].data.shift();
        graph.config.data.datasets[1].data.shift();
        graph.config.data.datasets[2].data.shift();
    }

    graph.config.data.labels.push(time + ':00');
    graph.config.data.datasets[0].data.push(formatNumber(data.energy_usage));
    graph.config.data.datasets[1].data.push(formatNumber(data.energy_production));
    graph.config.data.datasets[2].data.push(formatNumber(data.energy_netto));
    graph.update();

    label_string = '#' + label + '_average_label';
    document.querySelector(label_string).innerHTML = 'Netto Durchschnitt: ' + formatNumber(data.energy_netto_average) + ' kWh';

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
    graph.config.data.datasets[0].data.push(formatNumber(data.stromspeicher_prozent));
    graph.update();

    label_string = '#stromspeicher_label';
    document.querySelector(label_string).innerHTML = 'Speicher: ' + formatNumber(data.stromspeicher) + ' kWh';
}

const updateGas = (graph, time, data) => {
    if(graph.config.data.labels.length >= 30) {
        graph.config.data.labels.shift();
        graph.config.data.datasets[0].data.shift();
        graph.config.data.datasets[1].data.shift();
    }

    graph.config.data.labels.push(time + ':00');
    graph.config.data.datasets[0].data.push(formatNumber(data.energy));
    graph.config.data.datasets[1].data.push(formatNumber(data.production));
    graph.update();

    label_string = '#gaskraftwerk_average_label';
    document.querySelector(label_string).innerHTML = 'Produktion Durchschnitt: ' + formatNumber(data.average_production) + ' kWh';
    label_string = '#gaskraftwerk_money_label';
    document.querySelector(label_string).innerHTML = 'Gesamtkosten: ' + formatNumber(data.money_spent) + ' €';
    label_string = '#gaskraftwerk_speicher_label';
    document.querySelector(label_string).innerHTML = 'Wasserstoff Speicher: ' + formatNumber(data.speicher) + ' kWh';
}

let loop = async () => {
    const url = new URL('http://172.16.221.2:6969/getData');
    //const url = new URL('http://127.0.0.1:6969/getData')
    let res = await fetch(url);
    res = await res.json();
    if(res === null) return;
    res = res.data;


    updateSpeicher(stromspeicher_chart, res.time, res.general);
    updateGraph(general_energy_chart, 'general', res.time, res.general);
    updateGraph(central_energy_chart, 'central', res.time, res.central);
    updateGraph(wohnblock_energy_chart, 'wohnblock', res.time, res.wohnblock);
    updateGraph(krankenhaus_energy_chart, 'krankenhaus', res.time, res.krankenhaus);
    updateGas(gaskraftwerk_chart, res.time, res.GasEnergy)
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

const gaskraftwerk_chart = new Chart(
    document.querySelector('#gaskraftwerk_chart'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Verbrauch',
                    backgroundColor: 'red',
                    borderColor: 'red',
                    data: [],
                },
                {
                    label: 'Produktion',
                    backgroundColor: 'green',
                    borderColor: 'green',
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

setInterval(loop, 100);
