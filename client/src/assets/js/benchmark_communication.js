var benchmark_communication = {
  async fetch_running_benchmark(serverAddress) {
    return await fetch(`${serverAddress}/benchmarks/get_running_benchmark`)
        .then(response => response.json())
        .then(function(data) {
          if (data.result === "failure") {
            return ['none', 'none']
          }
          return [data.result.algorithm, data.result.benchmark]
        })
  },
  async fetch_benchmark_progress(serverAddress, algo, bench) {
    return await fetch(`${serverAddress}/benchmarks/progress`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({algorithm: algo, benchmark: bench})
    }).then(response => response.json())
  }
}

export default benchmark_communication