import { DatePicker as AntDatePicker }  from 'antd';


export const DatePicker = ({ input, meta, ...rest }: any) => {
    return(
    <AntDatePicker
        {...input}
        {...rest}
        onChange={(value: any) => input.onChange(value)}
        errorText={meta.touched ? meta.error : ''}
    />
)}
