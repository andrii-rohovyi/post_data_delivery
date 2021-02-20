import React from "react";

import { Form, Field } from 'react-final-form'
import {Form as AntForm} from 'antd';
import arrayMutators from 'final-form-arrays';
import { FieldArray } from 'react-final-form-arrays'
import {InputNumberComponent} from "./ui/InputNumberComponent";
import {InputComponent} from "./ui/Input";
import { CloseOutlined } from "@ant-design/icons";
import {DatePickerRange} from "./ui/DatePickerRange";
import {SelectComponent} from "./ui/InputSelect";


type PointType = {
  lat: number
  lng: number
  demand?: number
  time_window?: [Date, Date]
}
type Props = {
    points: PointType[],
    addPoint: (points: PointType[]) => void,
    result: PointType[][],
    setResult: (points: PointType[][]) => void
    setShowResult: (showResult: boolean) => void
}

type CourierType = {
    capacity: number,
    transport: string
}

type Values = {
    points: PointType[],
    couriers: CourierType[]
}
//demand: 2
//
// lat: 50.4486941427873
//
// lng: 30.52272858686755
//
// time_window: Array [ {…}, {…} ]


//"stores": [ {"location": [50.489023, 30.467676], "demand": 1, "time_window": [0, 1] }, {"location": [50.489030, 30.472075], "demand": 2, "time_window": [2, 3]} ],

type BackLocation = {
    location: number[]
    demand?: number,
    time_window: number[] | null
}

export const AddPointForm: React.FC<Props> = ({
  points,
  addPoint,
  result,
  setResult,
  setShowResult
}) => {

    const onSubmit = async (values: Values) => {
      // @ts-ignore
        console.log(values.couriers);
      const data = {
          central_store: {
              location: [values.points[0].lat, values.points[0].lng],
              time_window: values.points[0].time_window ? [values.points[0].time_window[0].valueOf(), values.points[0].time_window[1].valueOf()] : null
          },
          stores: values.points
              .map((point: PointType, index: number) => index !== 0 ? {
                  location: [point.lat, point.lng],
                  demand: point.demand,
                  time_window: point.time_window ? [point.time_window[0].valueOf(), point.time_window[1].valueOf()] : null
              } : null)
              .filter((value: BackLocation | null) => value !== null),
          couriers: values.couriers.map((courier, index) => ({
              pid: index,
              capacity: courier.capacity,
              transport: courier.transport
          }))
      }
      // @ts-ignore
        console.log(data, 'data');
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
          initialValues={{ points: (points.length && points) || [undefined, undefined], couriers: [undefined] }}
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
                <AntForm onFinish={handleSubmit}>
                  <div style={{padding: "16px", width: "53%", float: "left"}}>
                    <FieldArray name="points">
                  {({ fields }) =>
                    fields.map((name, index) => (
                      <div
                          key={name}
                          style={{
                              padding: "10px 0 10px 0",
                              position: "relative",
                              border: "2px solid rgb(255, 145, 0)",
                              borderRadius: "10px", margin: "10px 0 10px 0"
                          }}
                      >
                        <label>Point #{index + 1}</label>
                          <div>
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
                        </div>
                          {index !== 0 &&
                          <div style={{paddingTop: "10px"}}>
                              <label style={{display: "block"}}>Demand</label>
                              <Field
                                  name={`${name}.demand`}
                                  component={InputNumberComponent}
                                  placeholder="Demand"
                                  style={{width: "83%"}}
                              />
                          </div>
                          }
                          <div style={{paddingTop: "10px"}}>
                          <label>Time window</label>
                            <Field
                              name={`${name}.time_window`}
                              component={DatePickerRange}
                              showTime={true}
                              placeholder="Time window"
                              style={{marginRight: "5px"}}
                            />
                            <span
                                onClick={() => index !== 0 ? fields.remove(index) : {}}
                                style={{
                                    cursor: index !== 0 ? 'pointer' : 'not-allowed',
                                    marginLeft: "5px",
                                    position: "absolute",
                                    top: "49%",
                                    right: "5px"
                                }}
                            >
                                <CloseOutlined />
                            </span>
                              </div>
                      </div>
                    ))
                  }
                </FieldArray>
                  </div>
                    <div style={{padding: "16px", width: "40%", float: "right"}}>
                      <FieldArray
                          name="couriers"
                      >
                  {({ fields }) =>
                    fields.map((name, index) => (
                      <div
                          key={name}
                          style={{
                              padding: "10px 0 10px 0",
                              position: "relative",
                              border: "2px solid rgb(255, 145, 0)",
                              borderRadius: "10px", margin: "10px 0 10px 0"
                          }}
                      >
                        <label>Courier #{index + 1}</label>
                          <div>
                        <Field
                          name={`${name}.capacity`}
                          component={InputNumberComponent}
                          placeholder="Capacity"
                          style={{width: "40%", marginRight: "5px"}}
                        />
                        <Field
                          name={`${name}.transport`}
                          component={SelectComponent}
                          options={['driving', 'foot']}
                          placeholder="Transport"
                          style={{width: "40%", marginRight: "5px"}}
                        />
                    </div>
                      </div>

                          ))
                          }
                          </FieldArray>
                        <div className="buttons" style={{paddingTop: "20px", clear: "both"}}>
                      <button
                        type="button"
                        onClick={() => push('couriers', undefined)}
                      >
                        Add Courier
                      </button>
                      <button type="button" onClick={() => pop('couriers')}>
                        Remove Courier
                      </button>
                        </div>
                    </div>
                  <div className="buttons" style={{paddingTop: "20px", clear: "both"}}>
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
                </AntForm>
              </div>
    )}}
          />
    )
}