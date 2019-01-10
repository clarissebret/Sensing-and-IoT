var button = document.getElementById('myButton');

button.addEventListener('click', function() {
    console.log('Button was clicked');
    fetch('/', {method: 'POST'})
        .then(function (response) {
            if (response.ok) {
                console.log('Click was recorded');
                return;
            }
            throw new Error('Request failed.');
        })
        .catch(function (error) {
            console.log(error);
        });


    setInterval(function () {
        fetch('/', {method: 'GET'})
            .then(function (response) {
                if (response.ok) return response.json();
                throw new Error('Request failed.');
            })
            .then(function (data) {
                document.getElementById('showData').innerHTML = "Button was clicked lol times";
            })
            .catch(function (error) {
                console.log(error);
            });
    }, 1000);

});