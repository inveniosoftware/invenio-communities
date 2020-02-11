/*
 * This file is part of Invenio.
 * Copyright (C) 2017-2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React from "react";
import { useField, FieldArray } from "formik";
import CKEditor from "@ckeditor/ckeditor5-react";
import ClassicEditor from "@ckeditor/ckeditor5-build-classic";

export const TextInput = ({ label, ...props }) => {
  const [field, meta] = useField({ ...props, type: "text" });
  const error =
    meta.touched && meta.error ? (
      <div className="help-block">{meta.error}</div>
    ) : null;
  return(
    <div className={`form-group ${error ? "has-error" : ""}`}>
      <label htmlFor={props.id || props.name}>{label}</label>
      <input
        type="text"
        className="text-input form-control"
        {...field}
        {...props}
      />
      {error}
    </div>
  );
};

export const RichInput = ({ label, ...props }) => {
  const [{ value }, meta, { setValue, setTouched }] = useField({
    ...props,
    type: "text"
  });
  const error =
    meta.touched && meta.error ? (
      <div className="help-block">{meta.error}</div>
    ) : null;
  return (
    <div className={`form-group ${error ? "has-error" : ""}`}>
      <label htmlFor={props.id || props.name}>{label}</label>
      <CKEditor
        editor={ClassicEditor}
        data={value || ""}
        onChange={(event, editor) => {
          setValue(editor.getData());
        }}
        onBlur={(event, editor) => {
          setTouched(true);
        }}
        {...props}
      />
      {error}
    </div>
  );
};

export const SelectInput = ({ choices, label, ...props }) => {
  const [field, meta] = useField(props);
  return (
    <div className="form-group">
      <label htmlFor={props.id || props.name}>{label}</label>
      <select className="form-control" {...field} {...props}>
        {choices.map(choice => {
          return (
            <option key={choice.id} value={choice.id}>
              {choice.display}
            </option>
          );
        })}
      </select>
      {meta.touched && meta.error ? (
        <div className="help-block">{meta.error}</div>
      ) : null}
    </div>
  );
};


export const StringArrayInput = ({ choices, label, ...props }) => {
  const [ { value }, field, meta] = useField(props);
  return (
    <div className="form-group">
    <label htmlFor={props.id || props.name}>{label}</label>
    <FieldArray
      name={`${props.name}`}
      render={arrayHelpers => (
        <div className="form-group">
          {value && value.length > 0 ? (
            value.map( (alternate_identifier, index) => (
              <div key={index}>
                <TextInput label={`${props.name}.${index}`} name={`${props.name}[${index}]`} />
                <button
                  type="button"
                  onClick={() => arrayHelpers.remove(index)} // remove a friend from the list
                >
                  -
                </button>
                <button
                  type="button"
                  onClick={() => arrayHelpers.push('')} // insert an empty string at a position
                >
                  +
                </button>
              </div>
            ))
          ) : (
            <button type="button" onClick={() => arrayHelpers.push('')}>
              {/* show this when user has removed all alternate_identifiers from the list */}
              Add an alternate identifier
            </button>
          )}
          </div>
      )}
        />
    </div>
  )
}


export const ObjectArrayInput = ({ choices, label, ...props }) => {
  const [ { value }, field, meta] = useField(props);
  const keys_list = props.keys.split('/')
  var new_obj = {}
  keys_list.forEach(function(key) {
    new_obj[key] = '';
  });
  return (
    <div className="form-group">
    <label htmlFor={props.id || props.name}>{label}</label>
    <FieldArray
      name={`${props.name}`}
      render={arrayHelpers => (
        <div className="form-group">
          {value && value.length > 0 ? (
            value.map( (alternate_identifier, index) => (
              <div key={index}>
                {props.keys.split('/').map( (key, key_index) => (
                  <div key={key}>
                  <TextInput label={`${index}.${key}`} name={`${props.name}[${index}].${key}`} />
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => arrayHelpers.remove(index)} // remove a friend from the list
                >
                  -
                </button>
                <button
                  type="button"
                  onClick={() => arrayHelpers.push({ ...new_obj })} // insert an empty string at a position
                >
                  +
                </button>
              </div>
            ))
          ) : (
            <button type="button" onClick={() => arrayHelpers.push({ ...new_obj })}>
              {/* show this when user has removed all alternate_identifiers from the list */}
              Add an alternate identifier
            </button>
          )}
          </div>
      )}
        />
    </div>
  )
}
