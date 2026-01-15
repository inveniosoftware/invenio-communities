// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _isArray from "lodash/isArray";
import _isBoolean from "lodash/isBoolean";
import _isEmpty from "lodash/isEmpty";
import _isNull from "lodash/isNull";
import _isNumber from "lodash/isNumber";
import _isObject from "lodash/isObject";
import _mapValues from "lodash/mapValues";
import _pickBy from "lodash/pickBy";

/**
 * Remove empty values from an object or array recursively
 * @param {*} obj - The object or array to process
 * @returns {*} - The object or array with empty values removed
 */
export const removeEmptyValues = (obj) => {
  if (_isArray(obj)) {
    let mappedValues = obj.map((value) => removeEmptyValues(value));
    return mappedValues.filter((value) => {
      if (_isBoolean(value) || _isNumber(value)) {
        return value;
      }
      return !_isEmpty(value);
    });
  } else if (_isObject(obj)) {
    let mappedValues = _mapValues(obj, (value) => removeEmptyValues(value));
    return _pickBy(mappedValues, (value) => {
      if (_isArray(value) || _isObject(value)) {
        return !_isEmpty(value);
      }
      return !_isNull(value);
    });
  }
  return _isNumber(obj) || _isBoolean(obj) || obj ? obj : null;
};
