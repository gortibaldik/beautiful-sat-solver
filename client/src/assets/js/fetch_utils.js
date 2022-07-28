var fetch_json = {
  async post(address, body_dict) {
    return await fetch(address, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body_dict)
    }). then(response => response.json())
  }
}

export default fetch_json