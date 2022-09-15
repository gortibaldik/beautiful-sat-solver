<template>
  <div class="admin-up">
    <mdb-view>
    <mdb-card-title>
      <div>
        <mdb-icon icon="microchip" fas class="m-2 primary-color" size="3x"/>
        <section class="top-card-section">
          <mdb-row class="benchmarkSelector justify-content-center">{{defaultName}}</mdb-row>
          <mdb-row class="justify-content-center">
            <strong>
              <select
                class="browser-default custom-select algo-select"
                v-model="selectedNameData[index]"
              >
                <option selected disabled>{{defaultName}}</option>
                <option v-for="(algo, algo_index) in optionArray" :key="algo_index">
                  {{algo.name}}
                </option>
              </select>
            </strong>
          </mdb-row>
        </section>
      </div>
    </mdb-card-title>
    </mdb-view>
  </div>
</template>
<script>
import {
  mdbRow,
  mdbView,
  mdbCardTitle,
  mdbIcon,
} from 'mdbvue'
export default {
  name: 'algorithm-selector',
  components: {
    mdbRow,
    mdbView,
    mdbCardTitle,
    mdbIcon,
  },
  props: {
    defaultName: { required: true },
    selectedNameData: { required: true },
    index: { default: 0 },
    optionArray: { required: true }
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

.top-card-section {
  margin-top: -50px;
}

.benchmarkSelector {
  color: #999999;
  margin-bottom: -0.05rem;
  font-size: 13px;
}

.algo-select { 
  padding-bottom: 10px;
}

.admin-up .fas {
  box-shadow: 0 2px 9px 0 rgba(0, 0, 0, 0.2), 0 2px 13px 0 rgba(0, 0, 0, 0.19);
  padding: 1.2rem;
  font-size: 2.8rem;
  color: #fff;
  text-align: left;
  margin-right: 0.5rem;
  border-radius: 5px;
}

.admin-up {
  margin-left: -20px;
  margin-right: 4%;
  margin-top: -20px;
}
</style>