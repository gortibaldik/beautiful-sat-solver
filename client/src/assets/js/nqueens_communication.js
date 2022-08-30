// import fetch_json from "@/assets/js/fetch_utils"

var custom_run = {
  async fetchBasicInfoFromServer(serverAddress) {
    return await fetch(`${serverAddress}/nqueens/`)
      .then(response => response.json())
  },
}

export default custom_run