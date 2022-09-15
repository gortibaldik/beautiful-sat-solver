<template>
  <section v-if="optionArray && optionArray.length > 0">
    <mdb-row class="logSelector">
      {{title}}
    </mdb-row>
    <section
      v-for="(option, option_index) in optionArray"
      :key="option_index"
    >
      <mdb-row class="parameterSelector justify-content-between">
        <div>
        <a>{{option.name}}:</a>
        <div class="hintClass">{{option.hint}}</div>
        </div>
        <div v-if="option.type=='value'"
        class="align-self-center special-width">
          <input v-model="option.default" class="benchmarkPossibilities special-width"/>
        </div>
        <div v-if="option.type=='checkbox'"
        class="align-self-center">
          <input type="checkbox"
          :id="`${option_index}_${index}_checkbox`"
          v-model="option.default" />
        </div>
        <div v-if="option.type==='list'"
        class="align-self-center">
          <select class="browser-default custom-select benchmarkPossibilities special-width" v-model="option.default">
            <option v-for="value in option.options" :key="value">
              {{value}}
            </option>
          </select>
        </div>
        <div v-if="option.type=='multiline'"
        class="align-self-center">
          <textarea v-model="option.default" class="benchmarkPossibilities multiline-input"></textarea>
        </div> 
      </mdb-row>
    </section>
  </section>
</template>
<script>
import {
  mdbRow,
} from 'mdbvue'

export default {
  name: 'run-parameters',
  components: {
    mdbRow,
  },
  props: {
    optionArray: { required: true },
    title: { required: true },
    index: { default: 0 }
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

.parameterSelector {
  color: #999999;
  margin-bottom: -0.05rem;
  font-size: 13px;
  margin-left: 5px;
  margin-right: 5px;
}

.hintClass {
  display: none;
  margin-left: 10px;
}

a:hover + div.hintClass {
  display: block;
}

.benchmarkPossibilities {
  color: #1f71ff;
  font-size: 12px;
  padding: 0.1rem;
}

.special-width {
  width: 100px;
  max-width: 100px;
}

.multiline-input {
  width: 200px;
  min-width: 200px;
  height: 100px;
  min-height: 100px;
}
</style>