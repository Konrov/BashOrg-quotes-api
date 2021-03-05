package quotes

import (
	"log"
	"io/ioutil"
	"net/http"
	"html"
	"strings"
	"regexp"
	"strconv"
)


type Quote struct {
    Id int
    Date string
    Text string
}


func cleanHtml(raw_html string) string {

    re := regexp.MustCompile("<.*?>")
    return re.ReplaceAllString(raw_html, "")

}


func magic(txt string) string {
    
    lines_raw := strings.Split(txt, "\n")
    text := lines_raw[3]
    text = text[:len(text)-1]
    text = strings.Replace(text, "\"", "\\\"", -1)

    text = strings.Replace(text, "<' + 'br>", "\n", -1)

    text = text[8:]

    text = text[1:len(text)-1]

    text = cleanHtml(text)
    text = html.UnescapeString(text)
    return text

}


func getNewRawQuote() string {

    url := "https://bash.im/forweb/"
    res, err := http.Get(url)
    if err != nil {
        log.Fatal(err)
        return "none"
    }
    defer res.Body.Close()
    txt, err := ioutil.ReadAll(res.Body)
    if !(strings.Contains(string(txt), "borq")) {
        return "none"
    }
    return string(txt)

}


func getQuoteDetails(rawQuote string) Quote {

    pureText := magic(rawQuote)

    quote := Quote{}

    reDate := regexp.MustCompile(`\d{2}.\d{2}.\d{4}`)
    reId := regexp.MustCompile(`\#\d+`)

    datesFinded := reDate.FindAllString(pureText[:30], -1)
    quote.Date = datesFinded[0]

    pureText = strings.Replace(pureText[:30], quote.Date, " " + quote.Date + "\n", -1) + pureText[30:]

    // Remove 'Больше на bash.im!'
    pureText = pureText[:len(pureText)-26]
    pureTextSpl := strings.Split(pureText, "\n")

    idsFinded := reId.FindAllString(pureTextSpl[0], -1)
    qid, _ := strconv.Atoi(idsFinded[0][1:])
    quote.Id = qid

    quote.Text = strings.Join(pureTextSpl[1:], "\n")

    return quote

}

func NewQuote() Quote {

    q := getNewRawQuote()
    if q == "none" {
        return Quote{-1, "0", "0"}
    }
    return getQuoteDetails(q)

}

