const fetch = require('node-fetch') // "Fetch" HTTP req library
const CryptoJS = require('crypto-js') // Standard JavaScript cryptography library


const apiKey = 'Tl7CR0DqBuTjxqVcbaF4Bm1BKhHUzMFHFQirGgKFdDA' // const apiKey = 'paste key here'
const apiSecret = 'XpVzVtVnMrUIq91SjXiZx9iMYtYrDUUQbWDwIHJLI1M' // const apiSecret = 'paste secret here'

const apiPath = 'v2/auth/w/order/submit'// Example path

const nonce = (Date.now() * 1000).toString() // Standard nonce generator. Timestamp * 1000
const body = {
  type: 'MARKET',
  symbol: 'tPLANETS:UST',
  amount: '0.001',
} 

let signature = `/api/${apiPath}${nonce}${JSON.stringify(body)}` 
// Consists of the complete url, nonce, and request body
console.log(signature)
const sig = CryptoJS.HmacSHA384(signature, apiSecret).toString() 
// The authentication signature is hashed using the private key
console.log(sig)
fetch(`https://api.bitfinex.com/${apiPath}`, {
  method: 'POST',
  body: JSON.stringify(body),
  headers: {
    'Content-Type': 'application/json',
    'bfx-nonce': nonce,
    'bfx-apikey': apiKey,
    'bfx-signature': sig
  }
})
.then(res => res.json())
.then(json => console.log(json)) //Logs the response body
.catch(err => {
    console.log(err)
 })

