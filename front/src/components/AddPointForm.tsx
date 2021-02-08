import React from "react";

import { Form, Field } from 'react-final-form'
import arrayMutators from 'final-form-arrays';
import { FieldArray } from 'react-final-form-arrays'


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

type PointArrType = [number, number];

export const AddPointForm: React.FC<Props> = ({
  points,
  addPoint,
  result,
  setResult,
  setShowResult
}) => {

    const onSubmit = async (values: Values) => {
      // console.log(points, values.points.slice(1, values.points.length));
      // addPoint(points.concat(values.points.slice(1, values.points.length)));
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

      console.log(rawResponse);
      const content: PointArrType[][] = await rawResponse.json();
      const res: PointType[][] = new Array(content.length).fill([]);
      console.log(content, 'content');
      content.map((courierPoints, count) => courierPoints.map((point) => res[count].push({
              lat: point[0],
              lng: point[1]
      })))
      setResult(res);
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
                      component="input"
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
                          component="input"
                          placeholder="Lat"
                        />
                        <Field
                          name={`${name}.lng`}
                          component="input"
                          placeholder="Lon"
                        />
                        <span
                          onClick={() => fields.remove(index)}
                          style={{ cursor: 'pointer' }}
                        >
                            {' '} ❌
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