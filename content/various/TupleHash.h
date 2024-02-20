/**
 * Author: Unknown
 * Date: 2024-02-20
 * License: na
 * Source: na
 * Description: Function for hashing tuples
 * Status: not-tested
 */
#pragma once

struct CustomTupleHash {
    template <typename... Args>
    std::size_t operator()(const std::tuple<Args...>& tuple) const {
        return std::apply([](const Args&... args) {
            return ((std::hash<Args>{}(args) ^ ...));
        }, tuple);
    }
};
