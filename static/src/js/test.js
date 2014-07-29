/*
 *Test 
 * */

openerp.Rainsoft_Xiangjie = function(instance){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.Rainsoft_Xiangjie = {};

    instance.Rainsoft_Xiangjie.HomePage = instance.web.Widget.extend({
        start:function(){
            console.log("Test Success !!!");
        },
    });

    instance.web.client_actions.add('Rainsoft_Xiangjie.action_view_sms','instance.Rainsoft_Xiangjie.HomePage');

    instance.Rainsoft_Xiangjie.MyClass = instance.web.Class.extend({
        init:function(name){
            this.name=name;
        },
        say_hello:function(){
            console.log("Hello",this.name);
        },
    });

    var my_object = new instance.Rainsoft_Xiangjie.MyClass("Kevin Kong!!!");
    my_object.say_hello();
}
