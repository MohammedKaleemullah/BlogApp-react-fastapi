import React from "react";

const TextInput = ({ label, value, setValue, touched, setTouched, minLength,maxLength, type="text" }) => {
  const valid = value.length >= (minLength || 1) && value.length <= (maxLength || Infinity);
  return (
    <div>
      <label className="block font-semibold mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onBlur={() => setTouched(true)}
        className={`w-full border rounded px-3 py-2 ${
          touched && !valid ? "border-red-500" : "border-gray-300"
        }`}
      />
      {touched && !valid && (
        <p className="text-red-600 text-sm mt-1">
          {label} must be at least {minLength} characters long{maxLength ? ` and at most ${maxLength} characters long` : ''}.
        </p>
      )}
    </div>
  );
};

export default TextInput;
