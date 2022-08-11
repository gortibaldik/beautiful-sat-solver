import fetch_json from "@/assets/js/fetch_utils"

var results_communication = {
  async fetchBenchmarkResults(serverAddress) {
    return await fetch(`${serverAddress}/results/`)
      .then(response => response.json())
  },
  async fetchLogFile(serverAddress, log_file) {
    return await fetch_json.post(`${serverAddress}/results/get_log_file`, {
      log_file: log_file
    })
  },
  async fetchDeleteLogFile(serverAddress, log_file) {
    return await fetch_json.post(`${serverAddress}/results/remove_log_file`, {
      log_file: log_file
    })
  }
}

export default results_communication