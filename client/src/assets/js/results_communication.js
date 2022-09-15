import fetch_json from "@/assets/js/fetch_utils"

var results_communication = {
  async fetchBenchmarkResults(serverAddress) {
    return await fetch(`${serverAddress}`)
      .then(response => response.json())
  },
  async fetchLogFile(serverAddress, log_file) {
    return await fetch_json.post(`${serverAddress}get_log_file`, {
      log_file: log_file
    })
  },
  async fetchDeleteLogFile(serverAddress, log_file) {
    return await fetch_json.post(`${serverAddress}remove_log_file`, {
      log_file: log_file
    })
  }
}

export default results_communication