<template>
  <section id="profile">
    <mdb-row>
      <mdb-col md="12">
        <mdb-card class="card-with-logs rounded-border">
          <mdb-card-title class="blue darken-2 rounded-border text-center">
            <h4 class="h4-responsive text-white spaced-title">Standard Redis Worker Logs</h4>
          </mdb-card-title>
          <mdb-card-body>
            <div class="scrollbar-class">
              <mdb-scrollbar>
                {{stdLogs}}
              </mdb-scrollbar>
            </div>
          </mdb-card-body>
        </mdb-card>
      </mdb-col>
    </mdb-row>
    <mdb-row>
      <mdb-col md="12">
        <mdb-card class="card-with-logs rounded-border">
          <mdb-card-title class="blue darken-2 rounded-border text-center">
            <h4 class="h4-responsive text-white spaced-title">Error Redis Worker Logs</h4>
          </mdb-card-title>
          <mdb-card-body>
            <div class="scrollbar-class">
              <mdb-scrollbar>
                {{errorLogs}}
              </mdb-scrollbar>
            </div>
          </mdb-card-body>
        </mdb-card>
      </mdb-col>
    </mdb-row>
  </section>
</template>

<script>
import { 
  mdbRow,
  mdbCol,
  mdbCard,
  mdbCardTitle,
  mdbCardBody,
  mdbScrollbar,
} from 'mdbvue'

export default {
  name: 'Profile',
  components: {
    mdbRow,
    mdbCol,
    mdbCard,
    mdbCardTitle,
    mdbCardBody,
    mdbScrollbar,
  },
  data () {
    return {
      errorLogs: "<code>Nothing to show</code>",
      stdLogs: "<code>Nothing to show</code>"
    }
  }
}
</script>

<style scoped>
.card-with-logs {
  margin-top: 20px;
}
.rounded-border {
  border-radius: 5px;
}
.spaced-title {
  margin: 5px;
}
.scrollbar-class {
  height: 40vh
}
</style>
