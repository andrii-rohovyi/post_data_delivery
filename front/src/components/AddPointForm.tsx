import React from "react";

import { Form, Field } from 'react-final-form'
import arrayMutators from 'final-form-arrays';
import { FieldArray } from 'react-final-form-arrays'
import {InputNumberComponent} from "./ui/InputNumberComponent";
import {InputComponent} from "./ui/Input";
import { CloseOutlined } from "@ant-design/icons";


type PointType = {
  lat: number,
  lng: number
}
type Props = {
    points: PointType[],
    addPoint: (points: PointType[]) => void,
    result: PointType[][],
    setResult: (points: PointType[][]) => void
    setShowResult: (showResult: boolean) => void
}


type Values = {
    points: PointType[],
    deliveryman_cnt: number
}


export const AddPointForm: React.FC<Props> = ({
  points,
  addPoint,
  result,
  setResult,
  setShowResult
}) => {

    const onSubmit = async (values: Values) => {
      const data = {
          deliveryman_cnt: Number(values.deliveryman_cnt),
          head_location: Object.values(values.points[0]),
          stores_locations: values.points
              .map((point: PointType, index: number) => index !== 0 ? Object.values(point) : null)
              .filter((value: number[] | null) => value !== null)
      }
      const rawResponse = await fetch('http://localhost:8080', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        mode: 'cors',
        body: JSON.stringify(data)
      });

      const content: PointType[][] = await rawResponse.json();
      setResult(content);
      setShowResult(true)
    }
    return (
        <Form
          initialValues={{ points: (points.length && points) || [undefined, undefined] }}
          onSubmit={onSubmit}
          mutators={{
            ...arrayMutators
          }}
          render={({
            handleSubmit,
            form: {
              mutators: { push, pop }
            }, // injected from final-form-arrays above
            pristine,
            form,
            submitting,
            values,
          }) => {
          return (
              <div style={{padding: "10px"}}>
                <form onSubmit={handleSubmit}>
                  <div style={{border: "2px solid rgb(255, 145, 0)", borderRadius: "10px", padding: "16px"}}>
                      <label>Delivery Man {' '}</label>
                    <Field
                      name='deliveryman_cnt'
                      component={InputNumberComponent}
                      type="number"
                      placeholder="Delivery Man Count"
                    />
                    <FieldArray name="points">
                  {({ fields }) =>
                    fields.map((name, index) => (
                      <div key={name} style={{padding: "10px 0 10px 0"}}>
                        <label>Point #{index + 1}</label>
                        <Field
                          name={`${name}.lat`}
                          component={InputComponent}
                          placeholder="Lat"
                          disabled={index === 0}
                          style={{width: "40%", marginRight: "5px"}}
                        />
                        <Field
                          name={`${name}.lng`}
                          component={InputComponent}
                          placeholder="Lon"
                          disabled={index === 0}
                          style={{width: "40%", marginLeft: "5px"}}
                        />
                            <span
                                onClick={() => index !== 0 ? fields.remove(index) : {}}
                                style={{cursor: index !== 0 ? 'pointer' : 'not-allowed', marginLeft: "5px"}}
                            >
                                <CloseOutlined />
                            </span>
                      </div>
                    ))
                  }
                </FieldArray>
                  </div>
                  <div className="buttons" style={{paddingTop: "20px"}}>
                  <button
                    type="button"
                    onClick={() => push('points', undefined)}
                  >
                    Add Point
                  </button>
                  <button type="button" onClick={() => pop('points')}>
                    Remove Point
                  </button>
                    <button type="submit" disabled={submitting || pristine}>
                      Submit
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                          form.reset();
                      }}
                      disabled={submitting}
                    >
                      Reset
                    </button>
                  </div>
                </form>
              </div>
    )}}
          />
    )
}