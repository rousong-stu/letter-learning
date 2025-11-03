<template>
    <button>Pulse</button>
</template>

<style scoped>
    button {
        position: relative;
        z-index: 1;
        padding: 0.5em 1em;
        font-family: inherit;
        font-size: inherit;
        color: white;
        outline: none;
        background-color: hsl(236deg 32% 26%);
        border: none;
    }

    button:hover {
        cursor: pointer;
    }

    button::before {
        position: absolute;
        inset: 0;
        z-index: -1;
        content: '';
        border: 4px solid hsl(236deg 32% 26%);
        transform: scale(1);
        transform-origin: center;
    }

    button:hover::before {
        opacity: 0;
        transform: scale(1.75);
        transform-origin: center;
        transition: all 0.75s ease-in-out;
    }
</style>
