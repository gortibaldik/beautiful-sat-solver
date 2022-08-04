var redis_logs = {
  async fetch(serverAddress) {
    return await fetch(`${serverAddress}/redis_logs/`)
        .then(response => response.json())
        .then(function(data) {
          if (! ("errorLogs" in data) || ! ("stdLogs" in data) || data.result === "failure") {
            return ['failure', '']
          }
          return [data.errorLogs, data.stdLogs]
        })
  },
  async fetch_remove_std(serverAddress) {
    let fetch_address = `${serverAddress}/redis_logs/clear_std`
    console.log(fetch_address)
    return await fetch(fetch_address)
      .then(response => response.json())
  },
  async fetch_remove_error(serverAddress) {
    return await fetch(`${serverAddress}/redis_logs/clear_error`)
      .then(response => response.json())
  }
}

export default redis_logs