import { DatePicker as AntDatePicker }  from 'antd';


export const DatePicker = ({ input, meta, ...rest }: any) => {
    return(
    <AntDatePicker
        {...input}
        {...rest}
        format="YYYY-MM-DD"
        onChange={(value: any) => {
            console.log(value.valueOf());
            input.onChange(value)
        }}
        errorText={meta.touched ? meta.error : ''}
    />
)}
