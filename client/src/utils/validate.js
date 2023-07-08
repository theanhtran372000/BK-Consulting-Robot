export const validateUsername = (username) => {
    const regex = /^[a-zA-Z0-9]+$/
    const result = username.match(regex)
    
    if (!result) {
        return {
            success: false,
            message: 'Your username is not valid. Only characters A-Z, a-z and 0-9 are acceptable.'
        }
    }

    return {
        success: true,
        message: 'Username is valid.'
    }
}

export const validatePassword = (password) => {
    const regex = /^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{6,16}$/
    const result = password.match(regex)

    if (!result) {
        return {
            success: false,
            message: 'Password must have from 6 to 16 characters, and contains at least 1 number and 1 special character.'
        }
    }

    return {
        success: true,
        message: 'Password is valid.'
    }
}

export const validateName = (name) => {
    const regex = /^[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]*(?:[ ][A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]*)*$/
    const result = name.match(regex)

    if (!result) {
        return {
            success: false,
            message: 'Name must only contains only letters and spaces.'
        }
    }

    return {
        success: true,
        message: 'Name is valid.'
    }
}