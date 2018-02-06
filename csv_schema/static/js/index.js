import "babel-polyfill"
import {getModel} from './models';
import Vue from 'vue'
import _ from 'lodash'

Vue.component('add-many', {
  props: ['objectType'],
  template: "#add-many",
  delimiters: ['[[', ']]'],
  data: function(){
    let m = getModel(this.objectType);
    return {
      records: [new m()],
      model: m
    }
  },
  methods: {
    addAnother: function(){
      this.records.push(new this.model());
    },
    saveAll: function(){
      this.records.forEach((x) => {
        x.save();
      });
    },
  }
})

Vue.component('object-list', {
  props: ['objectType'],
  template: "#object-list",
  delimiters: ['[[', ']]'],
  data: function(){
    return {records: []};
  },
  methods: {
    remove: function(record){
      record.editing.delete().then((response) => {
        this.records = _.filter(this.records, (r) => {
          return r.id !== record.id;
        });
      });
      this.records.push(new this.model());
    },
  },
  mounted: function(){
    let promise = getModel(this.objectType).load();

    return promise.then((records) => {
      this.records = records;
    }).catch((error) => {
      alert(error);
    });
  }
});


new Vue({
  el: '#ncdr-container',
  delimiters: ['[[', ']]'],
  data: {
    selected: 2,
    options: [
      { id: 1, text: 'Hello' },
      { id: 2, text: 'World' }
    ]
  }
});
