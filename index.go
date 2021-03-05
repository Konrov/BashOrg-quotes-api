package main

import (
	"fmt"
	"log"
	"net/http"
	"encoding/json"
	"app/quotes"
)


var x_ver string = "0.1.1"
var x_source_url string = "https://github.com/Konrov"
var x_server string = "Go"


type APIErrMessage struct {
    Message string
    Description string
}

func main() {

    var port string = "8300"
    var host string = ":" + port
    fmt.Printf("Started serving at " + host + "\n")
	http.HandleFunc("/", index)
	http.HandleFunc("/random-quote", randomQuote)
	log.Fatal(http.ListenAndServe(host, nil))

}


func index(w http.ResponseWriter, r *http.Request) {

	w.Header().Set("X-Parser-Ver", x_ver)
	w.Header().Set("Location", x_source_url)
}


func randomQuote(w http.ResponseWriter, r *http.Request) {

    w.Header().Set("X-Parser-Ver", x_ver)
    w.Header().Set("X-Source-Url", x_source_url)
    w.Header().Set("Server", x_server)
    w.Header().Set("Content-Type", "application/json")
    data := quotes.NewQuote()
    if data.Id == -1 {
        dataerr := APIErrMessage{"Error", "Bash.im server has returned unexpected response"}
        json.NewEncoder(w).Encode(dataerr)
        return
    }
    json.NewEncoder(w).Encode(data)
    return

}
