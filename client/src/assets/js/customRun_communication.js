var custom_run = {
  async fetchStart(serverAddress, algo, bench, benchIn, logLevel) {
    return await fetch(`${serverAddress}/custom_run/start`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        algorithm:  algo,
        benchmark:  bench,
        entry:      benchIn,
        logLevel:   logLevel
      })
    }).then(response => response.json())
  },
  async fetchProgress(serverAddress, algo, bench, benchIn) {
    let data = null
    try {
      data = await fetch(`${serverAddress}/custom_run/is_finished`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          algorithm:  algo,
          benchmark:  bench,
          entry:      benchIn
        })
      }).then(response => response.json())
    } catch {
      data = {
        result: 'failure'
      }
    }
    return data.result
  },
  async fetchBasicInfoFromServer(serverAddress) {
    let data = await fetch(`${serverAddress}/custom_run/`)
      .then(response => response.json())
    return [data.benchmarks, data.algorithms, data.running_job]
  },
  async fetchCustomRunLogs(serverAddress) {
    let data = await fetch(`${serverAddress}/custom_run/get_logs`)
      .then(response => response.json())
    return data.result
  },
}

export default custom_run