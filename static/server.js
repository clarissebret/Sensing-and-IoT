// Connect to MongoDB database
console.log('Server-side code running');
var express = require('express');
var MongoClient = require('mongodb').MongoClient;
var url = "mongodb+srv://clarissebret:sensing-and-iot@cluster0-xrhtq.mongodb.net/";
var app = express();

// serve files from the public directory
app.use(express.static('public'));

// Add a helper to format timestamp data
function convertDate(str) {
    var dateParts = str.split(/-| |:/);
    var dateObj = new Date(+dateParts[0], +dateParts[1]-1, +dateParts[2], +dateParts[3], +dateParts[4]);
    return dateObj;
}

MongoClient.connect(url, function (err, db) {
    var dbo = db.db("ski");
    if (err) throw err;
    // start the express web server listening on 8080
    var server = app.listen(8080, '127.0.0.1', function (){
        console.log("Calling app.listen's callback function.");
        var host = server.address().address;
        var port = server.address().port;
        console.log('Example app listening at http://%s:%s', host, port);
    });

    // get the click data from the database
    app.get('/', function (req, res) {

        dbo.collection("user").find({_id: "Kenza"}, {projection: {_id: 0, activity: 1}})
            .toArray(function (err, json) {
            if (err) throw err;
            var labels = [], data = [];
            var results = json[0].activity;
            for (i in results) {
                labels.push(convertDate(i));
                data.push(results[i]);
            }
            if (err) return console.log(err);
            console.log(data)
            res.send(data);
        });
    });
});

