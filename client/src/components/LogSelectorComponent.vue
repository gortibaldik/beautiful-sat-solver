<template>
  <section>
    <mdb-row class="logSelector">
      SELECT LOG LEVEL:
    </mdb-row>
    <mdb-row class="justify-content-center">
      <div class="custom-control custom-radio custom-control-inline">
        <input type="radio" :name="`radioLogLevel__${index}`" class="custom-control-input" :id="`${index}__LogLevelDebug`" value="DEBUG" v-model="selectedLogLevels[index]">
        <label class="custom-control-label" :for="`${index}__LogLevelDebug`">DEBUG</label>
      </div>
      <div class="custom-control custom-radio custom-control-inline">
        <input type="radio" :name="`radioLogLevel__${index}`" class="custom-control-input" :id="`${index}__LogLevelInfo`" value="INFO" v-model="selectedLogLevels[index]">
        <label class="custom-control-label" :for="`${index}__LogLevelInfo`">INFO</label>
      </div>
      <div class="custom-control custom-radio custom-control-inline">
        <input type="radio" :name="`radioLogLevel__${index}`" class="custom-control-input" :id="`${index}__LogLevelWarning`" value="WARNING" v-model="selectedLogLevels[index]">
        <label class="custom-control-label" :for="`${index}__LogLevelWarning`">WARNING</label>
      </div>
    </mdb-row>
  </section>
</template>
<script>
import {
  mdbRow,
} from 'mdbvue'
export default {
  name: 'log-selector',
  components: {
    mdbRow,
  },
  props: {
    index: { default: 0 },
    selectedLogLevels: { required: true }
  },
  data() {
    return {}
  }
}
</script>
<style scoped>
.logSelector {
  color: #999999;
  margin-bottom: -0.05rem;
  font-size: 13px;
  margin-left: 0px;
}
</style>