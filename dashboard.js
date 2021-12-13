let loop = async () => {
    const url = new URL('http://localhost:6969/getData');

    let res = await fetch(url);
    res = await res.json();
    console.log(res);

    if(res === null) return;

    if(myCharto.config.data.labels.length >= 30) {
        myCharto.config.data.labels.shift();
        myCharto.config.data.datasets[0].data.shift();
    }

    myCharto.config.data.labels.push(res.time + ':00');
    myCharto.config.data.datasets[0].data.push(res.energy);
    myCharto.update();

}

const labels = [

];
const data = {
    labels: labels,
    datasets: [{
        label: 'My First dataset',
        backgroundColor: 'rgb(255, 99, 132)',
        borderColor: 'rgb(255, 99, 132)',
        data: [],
    }]
};

const options = {
    scales: {
        yAxes: {
            beginAtZero: true,
            max: 10000
        }
    },
    animation: {
        easing: 'linear'
    }
};

const config = {
    type: 'line',
    data: data,
    options: options
};

const myCharto = new Chart(
    document.getElementById('myChart'),
    config
);

setInterval(loop, 1000);
