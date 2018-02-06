import 'whatwg-fetch'
import Cookies from 'js-cookie';
const csrftoken = Cookies.get('csrftoken');
const fetchHeaders = new Headers({
    "X-CSRFToken": csrftoken,
    "Accept": "application/json",
    "Content-Type": "application/json"
})

class Editing{
  constructor(editingFields, url){
    this.editMode = false;
    this.editingFields = editingFields;
    this.url = url;
  }
  populate(args){
    this.editingFields.forEach(x => {
      this[x] = args[x];
    });
    this.editMode = true;
  }
  delete(){
    this.loading = true;
    let editUrl = this.url + this.id + "/";
    return fetch(editUrl, {
      method: 'DELETE',
      credentials: 'include',
      headers: fetchHeaders
    }).then(() => {
      this.loading = false;
    });
  }
  save(){
    let result = new Promise((resolve) => {
      let postData = {};
      let editUrl = this.url;
      let method = "POST";
      if(this.id){
        method = "PUT";
        editUrl = this.url + this.id + "/";
      }
      var self = this;
      this.loading = true;
      this.editingFields.forEach(field => {
        postData[field] = this[field]
      });

      fetch(editUrl, {
        method: method,
        body: JSON.stringify(postData),
        credentials: 'include',
        headers: fetchHeaders
      }).then((response) => {
        response.json().then(function(update){
          self.editMode = false;
          self.loading = false;
          resolve(update);
        });
      });
    });

    return result;
  }
  cancel(){
    this.editMode = false;
  }
}

class Record {
  constructor(args) {
    this.fields = this.getFields();
    if(args){
      this.update(args);
    }
    this.editing = new Editing(
      this.fields, this.constructor.getUrl()
    );
  }
  getFields(){
    throw "getFields needs to be implemented";
  }
  static getApiName(){
    throw "getApiName needs to be implemented";
  }
  static getUrl(){
    return "/api/" + this.getApiName() + "/";
  }
  update(args){
    this.fields.forEach(x => {
      this[x] = args[x];
    });
  }
  edit (){
    this.editing.populate(this);
  }
  save(){
    this.editing.save().then((response) => {
      this.update(response)
    })
  }
  static load(){
    var self = this;
    let result = new Promise((resolve, reject) => {
      let url = this.getUrl();

      fetch(url, {headers: fetchHeaders, credentials: 'include'}).then(function(data){
        if(data.status < 400){
          data.json().then(function(rawRecords){
            let databases = rawRecords.results.map(function(rawDatabase){
              return new self(rawDatabase);
            });
            resolve(databases);
          });
        }
        else{
          reject("fail");
        }
      });
    });
    result.catch(function(){});

    return result;
  }
}

class Database extends Record{
  getFields(){
    return ['name', 'database', 'id', "description"];
  }
  static getApiName(){
    return "database";
  }
}

class Table extends Record{
  getFields(){
    return ['name', 'database', 'id', "description", "date_range"];
  }
  static getApiName(){
    return "table";
  }
}

class Grouping extends Record{
  getFields(){
    return ['name', 'id'];
  }
  static getApiName(){
    return "grouping";
  }
}

class Column extends Record{
  getFields(){
    return [
      'name',
      'description',
      'data_type',
      'is_derived_item',
      'derivation',
      'tables',
      'grouping',
      'link',
      'id'
    ];
  }
  static getApiName(){
    return "column";
  }
}

var getModel = function(someName){
  // change this to just pull from window
  if(someName === "table"){
    return Table;
  }
  if(someName === "database"){
    return Database;
  }
  if(someName === "grouping"){
    return Grouping;
  }
  if(someName === "column"){
    return Column;
  }
  alert('unable to figure out what the object is');
  throw "unknown model name";
}


export {Database, Table, getModel}
