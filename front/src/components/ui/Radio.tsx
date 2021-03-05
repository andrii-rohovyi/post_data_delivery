import { Radio as AntRadio } from 'antd';
import {CarFilled, ShoppingFilled} from "@ant-design/icons";
import React from "react";


const checkedIcons = {
    'car': <CarFilled style={{color: "#1890ff"}} width="24px" height="24px"/>,
    'shopping': <ShoppingFilled style={{color: "#1890ff"}} />
}

const unCheckedIcons = {
    'car': <CarFilled />,
    'shopping': <ShoppingFilled />
}


export const Radio = ({ input, meta, icon, ...rest }: any) => {
    return(
      <AntRadio.Button
          {...input}
          {...rest}
          value={icon}
          // style={{
          //     border: "none",
          //     background: "none"
          // }}
          buttonStyle="outlined"
          onChange={(e) => {
              input.onChange(input.value);
          }}
      >
          {input.checked ?
              // @ts-ignore
            checkedIcons[input.value] :
              // @ts-ignore
            unCheckedIcons[input.value]

          }
      </AntRadio.Button>
)}
