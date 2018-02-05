import {Database} from './models';
import Vue from 'vue'
import _ from 'lodash'


let ol = Vue.component('object-list', {
  props: [],
  template: "#object-list",
  delimiters: ['[[', ']]'],
  methods: {
    // appendToRequest: function(apiName, field, value){
    //   var currentHref = window.location.href;
    //   if(currentHref.indexOf("?") === -1){
    //     return currentHref + "?" + apiName + "__" + field + "=" + value;
    //   }
    //   else{
    //     return currentHref + "&" + apiName + "__" + field + "=" + value;
    //   }
    // }
  },
  data: function(){
    return {databases: []};

  },
  mounted: function(){
    return Database.load().then((databases) => {
      this.databases = databases;
    }).catch((error) => {
      alert(error);
    });
  }
});


new Vue({
  el: '#ncdr-container',
  delimiters: ['[[', ']]'],
});
