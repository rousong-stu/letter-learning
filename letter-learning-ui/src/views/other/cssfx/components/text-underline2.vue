<template>
    <span>Underline</span>
</template>

<style scoped>
    span {
        position: relative;
    }

    span::before {
        position: absolute;
        right: 0;
        bottom: 0;
        left: 0;
        height: 2px;
        content: '';
        background-color: #1890ff;
        transform: scaleX(1);
        transform-origin: bottom left;
        transition: transform 0.3s ease-in-out;
    }

    span:hover::before {
        transform: scaleX(0);
        transform-origin: bottom right;
    }
</style>
