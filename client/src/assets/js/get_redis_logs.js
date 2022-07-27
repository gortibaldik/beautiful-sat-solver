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
}

export default redis_logs