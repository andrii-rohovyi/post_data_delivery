import React from "react";

import { Form, Field } from 'react-final-form'
import {Button, Form as AntForm, Radio as AntRadio, TimePicker} from 'antd';
import arrayMutators from 'final-form-arrays';
import { FieldArray } from 'react-final-form-arrays'
import {InputNumberComponent} from "./ui/InputNumberComponent";
import {InputComponent} from "./ui/Input";
import {CarFilled, CloseCircleFilled, CloseOutlined, PlusCircleTwoTone, ShoppingFilled} from "@ant-design/icons";
import {DatePickerRange} from "./ui/DatePickerRange";
import {SelectComponent} from "./ui/InputSelect";
import {DatePicker} from "./ui/DatePicker";
import {Radio} from "./ui/Radio";
import {DropdownNumber} from "./ui/DropdownNumber";
import {RangeTimePicker} from "./ui/RangeTimePicker";

var moment = require('moment');

type PointType = {
  lat: number
  lng: number
  demand?: number
  time_window?: [moment.Moment, moment.Moment]
}
type Props = {
    points: PointType[],
    addPoint: (points: PointType[]) => void,
    result: Response,
    setResult: (points: Response) => void
    setShowResult: (showResult: boolean) => void
}

type CourierType = {
    capacity: number,
    transport: string
}

type Values = {
    points: PointType[],
    couriers: CourierType[],
    deliveryDate: moment.Moment
}
//demand: 2
//
// lat: 50.4486941427873
//
// lng: 30.52272858686755
//
// time_window: Array [ {…}, {…} ]

type Response = {
    routes: PointType[][],
    dropped_nodes: PointType[][]
}

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
    const required = (value: any) => (value ? undefined : 'Required');

    const onSubmit = async (values: Values) => {
      const data = {
          central_store: {
              location: [values.points[0].lat, values.points[0].lng],
              time_window: values.points[0].time_window ?
                  [
                      // @ts-ignore
                      moment(values.deliveryDate.format("YYYY-MM-DD") + " " + values.points[0].time_window[0].format('HH:mm'), 'YYYY-MM-DD HH:mm').valueOf(),
                      // @ts-ignore
                      moment(values.deliveryDate.format("YYYY-MM-DD") + " " + values.points[0].time_window[1].format('HH:mm'), 'YYYY-MM-DD HH:mm').valueOf(),
                  ] : null
          },
          stores: values.points
              .map((point: PointType, index: number) => index !== 0 ? {
                  location: [point.lat, point.lng],
                  demand: point.demand,
                  time_window: point.time_window ? [
                      moment(values.deliveryDate.format("YYYY-MM-DD") + " " + point.time_window[0].format('HH:mm'), 'YYYY-MM-DD HH:mm').valueOf(),
                      moment(values.deliveryDate.format("YYYY-MM-DD") + " " + point.time_window[1].format('HH:mm'), 'YYYY-MM-DD HH:mm').valueOf(),
                  ] : null
              } : null)
              .filter((value: BackLocation | null) => value !== null),
          couriers: values.couriers.map((courier, index) => ({
              pid: index,
              capacity: Number(courier.capacity),
              transport: courier.transport
          }))
      }
      console.log(data.central_store.time_window, 'central time_window');
      const rawResponse = await fetch('http://localhost:8080', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        mode: 'cors',
        body: JSON.stringify(data)
      });

      const content: Response = await rawResponse.json();
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
              <div style={{paddingLeft: "16px", paddingTop: "24px", textAlign: "left"}}>
                  {console.log(values, 'val')}
                  <label style={{
                      fontFamily: "DM Sans",
                      fontStyle: "normal",
                      fontWeight: "bold",
                      fontSize: "14px",
                      lineHeight: "24px",
                      color: "#7B8AA1"
                  }}
                  >
                      DELIVERY DATE
                  </label>
                  {
                      // @ts-ignore
                      console.log(values.deliveryDate ? moment(values.deliveryDate, 'YYYY-MM-DD').valueOf() : "pdior")
                  }
                  <div>
                        <Field
                          name="deliveryDate"
                          component={DatePicker}
                          placeholder="Select date"
                          style={{width: "55%", marginTop: "8px"}}
                          validate={required}
                        />
                  </div>
                  <div
                      style={{
                          fontFamily: "DM Sans",
                          fontStyle: "normal",
                          fontWeight: "bold",
                          fontSize: "14px",
                          lineHeight: "24px",
                          color: "#7B8AA1",
                          marginTop: "48px"
                      }}
                  >
                      COURIERS
                  </div>
                  <FieldArray name="couriers">
                  {({ fields }) =>
                    fields.map((name, index) => (
                        <>
                          <div style={{background: "#F7F9FC", borderRadius: "8px", marginRight: "16px", marginBottom: "8px"}}>
                              <p style={{
                                  display: "inline-block",
                                  fontFamily: "DM Sans",
                                  fontStyle: "normal",
                                  fontWeight: "bold",
                                  fontSize: "14px",
                                  lineHeight: "24px",
                                  paddingTop: "21px",
                                  marginLeft: "21px",
                                  paddingBottom: "3px",
                                  marginRight: "46px",
                              }}>
                                  Courier {index + 1}
                              </p>
                                <Field
                                  type="radio"
                                  name={`${name}.transport`}
                                  component={Radio}
                                  value='driving'
                                  // style={{width: "55%", marginTop: "8px", display: "inline-block"}}
                                />
                                <Field
                                  type="radio"
                                  name={`${name}.transport`}
                                  component={Radio}
                                  value='walking'
                                  // style={{width: "55%", marginTop: "8px", display: "inline-block"}}
                                />
                                <Field
                                  name={`${name}.capacity`}
                                  component={DropdownNumber}
                                  initialValue={100}
                                  style={{marginLeft: "30px"}}
                              />
                              <p style={{marginLeft: "10px", color: "#7B8AA1", display: "inline-block"}}>kg</p>
                          </div>
                  </>
                      ))
                  }

                  </FieldArray>

                  <p
                      style={{
                      alignItems: "baseline",
                      display: "flex",
                      flexDirection: "row",
                      justifyContent: "center",
                      paddingTop: "12px",
                  }}
                      onClick={() => push('couriers', undefined)}
                  >
                      <PlusCircleTwoTone style={{display: "inline-block", cursor: "pointer"}} />
                      <p style={{color: "#1890ff", marginLeft: "4px", cursor: "pointer"}}> Add courier </p>
                  </p>

                  <div style={{border: "1px solid #E9EDF4"}} />
                  <div style={{
                      fontFamily: "DM Sans",
                      fontStyle: "normal",
                      fontWeight: "bold",
                      fontSize: "14px",
                      lineHeight: "24px",
                      color: "#7B8AA1",
                      marginTop: "48px"
                  }}
                  >
                      DELIVERY POINTS
                  </div>

                  <div style={{marginRight: "16px"}}>
                      <FieldArray name="points">
                  {({ fields }) =>
                    fields.map((name, index) => (
                        <div style={{position: "relative", marginBottom: "8px", background: "#F7F9FC", borderRadius: "8px",}}>
                      <p style={{
                          display: "block",
                          fontFamily: "DM Sans",
                          fontStyle: "normal",
                          fontWeight: "bold",
                          fontSize: "14px",
                          lineHeight: "24px",
                          paddingTop: "21px",
                          marginLeft: "21px",
                          paddingBottom: "3px",
                          marginRight: "46px",
                      }}>
                          {index === 0 ? "Starting Point" : `Point ${index + 1}`
                          }
                      </p>
                      <Field
                          name={`${name}.lat`}
                          component={InputNumberComponent}
                          style={{width: "16%", marginBottom: "16px", marginLeft: "16px"}}
                      />
                      <Field
                        name={`${name}.lng`}
                        component={InputNumberComponent}
                          style={{width: "16%", marginLeft: "4px", marginRight: "12px"}}
                      />
                      <Field
                        name={`${name}.time_window`}
                        component={RangeTimePicker}
                          // style={{marginLeft: "45%"}}
                      />
                      {index !== 0 &&
                          <>
                          <Field
                              name={`${name}.demand`}
                              component={InputNumberComponent}
                              style={{marginLeft: "30px"}}
                          />
                          <p style={{marginLeft: "10px", color: "#7B8AA1", display: "inline-block"}}>kg</p>
                              <CloseCircleFilled
                                  onClick={() => index !== 0 ? fields.remove(index) : {}}
                                  style={{
                                      position: "absolute",
                                      top: "12px",
                                      right: "12px",
                                      fontSize: "24px",
                                      color: "#7B8AA1"
                                  }}
                              />
                          </>
                      }
                      </div>
                      ))
                  }
                </FieldArray>
                      <p
                          onClick={() => push('points', undefined)}
                          style={{
                              alignItems: "baseline",
                              display: "flex",
                              flexDirection: "row",
                              justifyContent: "center",
                              paddingTop: "12px",
                          }}

                      >
                      <PlusCircleTwoTone style={{display: "inline-block", cursor: "pointer"}} />
                      <p style={{color: "#1890ff", marginLeft: "4px", cursor: "pointer"}}> Add point </p>
                  </p>

                  </div>

                  <div style={{float: "right", marginRight: "16px"}}>
                      <Button
                          type="default"
                          size="large"
                          onClick={() => {
                              form.reset();
                          }}
                          disabled={submitting}
                      >
                          Reset
                      </Button>
                      <Button
                          type="primary"
                          size="large"
                          style={{marginLeft: "16px"}}
                          onClick={handleSubmit}
                      >
                          Create plan
                      </Button>
                  </div>
              </div>
    )}}
          />
    )
}