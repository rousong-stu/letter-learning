<template>
    <button>Bubble</button>
</template>

<style scoped>
    button {
        position: relative;
        z-index: 1;
        padding: 0.5em 1em;
        overflow: hidden;
        font-family: inherit;
        font-size: inherit;
        color: white;
        outline: none;
        background-color: hsl(236deg 32% 26%);
        border: none;
        transition: color 0.4s ease-in-out;
    }

    button::before {
        position: absolute;
        bottom: 100%;
        left: 100%;
        z-index: -1;
        width: 1em;
        height: 1em;
        content: '';
        background-color: #1890ff;
        border-radius: 50%;
        transform: translate3d(-50%, 50%, 0) scale3d(0, 0, 0);
        transform-origin: center;
        transition: transform 0.45s ease-in-out;
    }

    button:hover {
        color: #fff;
        cursor: pointer;
    }

    button:hover::before {
        transform: translate3d(-50%, 50%, 0) scale3d(15, 15, 15);
    }
</style>
