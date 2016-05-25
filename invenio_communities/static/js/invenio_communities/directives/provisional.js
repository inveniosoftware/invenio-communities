/*
 * This file is part of Invenio.
 * Copyright (C) 2016 CERN.
 *
 * Invenio is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * Invenio is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Invenio; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 *
 * In applying this license, CERN does not
 * waive the privileges and immunities granted to it by virtue of its status
 * as an Intergovernmental Organization or submit itself to any jurisdiction.
 */

define([], function(){
  function invenioSearchResultsProvisional($http, $q) {
    "use strict";

    // Functions

    /**
     * Force apply the attributes to the scope
     * @memberof invenioSearchResults
     * @param {service} scope -  The scope of this element.
     * @param {service} element - Element that this direcive is assigned to.
     * @param {service} attrs - Attribute of this element.
     * @param {service} http - Angular HTTP requests service.
     * @param {invenioSearchController} vm - Invenio search controller.
     */
    function link(scope, element, attrs, vm) {
      scope.communityCurationEndpoint = attrs.communityCurationEndpoint;
      scope.recordTemplate = attrs.recordTemplate;
      scope.CommunitieshandleClick = function(action, record) {
          // scope.isPressed=true
          function ajax_callback(record, result)
          {
              var element = document.querySelector("#communities-rec-" + record.id);
              var msg_elt = document.querySelector("#js-flash-message");
              msg_elt.classList.remove("hidden");
              msg_elt.classList.remove("alert-danger");
              msg_elt.classList.remove("alert-success");
              msg_elt.classList.remove("alert-info");
              var success = true;
              if (result.status !== 200 || !result.data.status)
              {
                  success = false;
                  msg_elt.classList.add("alert-danger");
              }
              else
                  msg_elt.classList.add("alert-" + result.data.status);
              if (result.data.msg)
                  msg_elt.querySelector("#js-flash-message-text").textContent = result.data.msg;
              else
                  msg_elt.querySelector("#js-flash-message-text").textContent = "Server Error";
              if (success)
                  element.parentElement.removeChild(element);
              else
              {
                  var btns = element.querySelectorAll("#curate_" + record.id + " a.btn");
                  for (var i = 0; i < btns.length; i++)
                  {
                      btns[i].classList.remove("btn-danger");
                      btns[i].classList.remove("btn-success");
                      btns[i].removeAttribute("disabled");
                  }
              }
          }
          $http({
            method: 'POST',
            url: scope.communityCurationEndpoint,
            data: {
              'recid': record.id,
              'action': action,
            },
            headers: {'Content-Type': 'application/json'},
          }).then(function successCallback(result) {
                ajax_callback(record, result);
            }, function errorCallback(result) {
                ajax_callback(record, result);
            });
        };
    }

    /**
     * Choose template for search loading
     * @memberof invenioSearchREsults
     * @param {service} element - Element that this direcive is assigned to.
     * @param {service} attrs - Attribute of this element.
     * @example
     *    Minimal template `template.html` usage
     *    <div ng-repeat="record in invenioSearchResults track by $index">
     *      <div ng-include="recordsTemplate"></div>
     *    </div>
     *
     *    Minimal `recordsTemplate`
     *    <h2>{{ record.title }}</h2>
     */
    function templateUrl(element, attrs) {
      return attrs.template;
    }

    ////////////
    return {
      restrict: 'AE',
      scope: false,
      templateUrl: templateUrl,
      link: link,
    };
  }
  invenioSearchResultsProvisional.$inject = ['$http', '$q'];
  return invenioSearchResultsProvisional;
});
